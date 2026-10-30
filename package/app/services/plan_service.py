"""
Business logic for each user's active plan: session views, Garmin sync
(rolling window), activity reconciliation, statuses, regeneration and closing.

A plan finishes on its own two days after the race (margin to record the activity):
it becomes "completed" and stays in the history. Closing it earlier leaves it as "cancelled".

Only sessions in the next SYNC_WINDOW_DAYS days are uploaded to Garmin. This way the watch does not
fill up and future sessions can change (VDOT, language, adjustments) without touching Garmin.
"""
import json
import logging
import threading
import time
from functools import lru_cache
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session, joinedload

from app.core.database import SessionLocal, checkpoint
from app.engine.periodization import generate_plan, tuneup_weeks, week_of, week_phases
from app.engine.stats import (
    CHRONIC_DAYS, EFFICIENCY_TYPES, FORM_TYPES, INTENSITY_WINDOW_DAYS, adherence, efficiency_trend, form_estimate,
    hard_fraction, intensity_distribution, load_status, meters_per_beat, pace_check, session_load, session_vdot,
    work_pace, work_summary,
)
from app.engine.vdot import DISTANCE_METERS, get_vdot_from_race, predict_race_time_range
from app.engine.workouts import WORK_KINDS, expected_pace, expected_work_pace, garmin_payload, render, summarize
from app.models.schemas import ActivityLog, GarminDeletion, PlanRace, TrainingPlan, UserProfile, VdotHistory, Workout
from app.services.garmin_client import GarminAccount, garmin_accounts

logger = logging.getLogger("plan_service")

SYNC_WINDOW_DAYS = 10
MISSED_GRACE_DAYS = 1  # margin for the activity to arrive from the watch
MATCH_TOLERANCE_DAYS = 1
MATCH_MIN_FRACTION = 0.5  # minimum distance (relative to planned) for an activity to complete a session
MAX_DELETE_ATTEMPTS = 48  # retries (one per hourly cycle): about 2 days
LAPS_PER_CYCLE = 5  # lap reads per cycle, to avoid overloading Garmin
FINISH_AFTER_DAYS = MISSED_GRACE_DAYS + 1  # the plan closes itself this many days after the race
B_RESULT_DAYS = 14  # days after a B race during which adjusting the VDOT from its time is offered
B_RESULT_MIN_FRACTION = 0.9  # minimum recorded distance (relative to official) to trust the time
B_RESULT_MIN_CHANGE = 0.5  # VDOT change below which nothing is proposed

_sync_lock = threading.Lock()


class SyncStatus:
    """In-memory sync state per user, so the UI can tell "sending to watch"
    from "failed". Lost on restart (the hourly cycle syncs again)."""
    STALE_SEC = 300  # an older "syncing" mark is ignored

    def __init__(self):
        self._since: Dict[int, float] = {}
        self._errors: Dict[int, int] = {}
        self._lock = threading.Lock()

    def start(self, user_id: int):
        with self._lock:
            self._since[user_id] = time.time()

    def finish(self, user_id: int, errors: Optional[int] = None):
        with self._lock:
            self._since.pop(user_id, None)
            if errors is not None:
                self._errors[user_id] = errors

    def syncing(self, user_id: int) -> bool:
        since = self._since.get(user_id)
        return since is not None and time.time() - since < self.STALE_SEC

    def failed(self, user_id: int) -> bool:
        return self._errors.get(user_id, 0) > 0


sync_status = SyncStatus()


# --- Queries -------------------------------------------------------------

def get_active_plan(db: Session, user_id: int) -> Optional[TrainingPlan]:
    return db.query(TrainingPlan).filter(TrainingPlan.user_id == user_id, TrainingPlan.status == "active").first()


def account(plan: TrainingPlan) -> GarminAccount:
    return garmin_accounts.get(plan.user_id)


def language(plan: TrainingPlan) -> str:
    return plan.user.preferred_language or "es"


def plan_vdot(plan: TrainingPlan) -> float:
    return plan.vdot or plan.user.calculated_vdot


def plan_adjustments(plan: TrainingPlan) -> Tuple[float, Set[int]]:
    adj = json.loads(plan.adjust_json) if plan.adjust_json else {}
    return float(adj.get("volume_factor", 1.0)), set(adj.get("deload_weeks", []))


def b_races(plan: TrainingPlan) -> List[Tuple[date, str]]:
    return [(r.race_date, r.distance) for r in plan.races]


def phases_for(plan: TrainingPlan) -> List[str]:
    _, deloads = plan_adjustments(plan)
    return week_phases(plan.total_weeks, plan.target_distance, plan.injury_history, deloads,
                       tuneup_weeks(plan.start_date, b_races(plan)))


def current_week(plan: TrainingPlan, today: Optional[date] = None) -> int:
    return max(1, min(plan.total_weeks, week_of(plan.start_date, today or date.today())))


# --- Session views -------------------------------------------------------------

@lru_cache(maxsize=512)
def _expected_pace(spec_json: str, vdot: float) -> float:
    return expected_pace(json.loads(spec_json), vdot)


@lru_cache(maxsize=512)
def _expected_work_pace(spec_json: str, vdot: float) -> float:
    return expected_work_pace(json.loads(spec_json), vdot)


@lru_cache(maxsize=512)
def _work(laps_json: str) -> Optional[Dict[str, Any]]:
    return work_summary(json.loads(laps_json))


def log_work(w: Workout, log: Optional[ActivityLog]) -> Optional[Dict[str, Any]]:
    """Recorded work blocks of a tempo or intervals (None if there are no usable laps)."""
    if w.session_type not in WORK_KINDS or not (log and log.laps_json):
        return None
    return _work(log.laps_json)


def session_pace_check(w: Workout, log: Optional[ActivityLog], vdot: float) -> Optional[Dict[str, Any]]:
    """Actual vs expected pace of a completed session (None if there is no data to compare).
    For tempo and intervals the work blocks are compared if Garmin recorded them (basis = "work")."""
    if w.status != "completed" or not (log and log.avg_pace_sec_km):
        return None
    work = log_work(w, log)
    if work:
        check = pace_check("work", _expected_work_pace(w.spec_json, w.vdot or vdot), work_pace(work))
        if check:
            return {**check, "basis": "work"}
    check = pace_check(w.session_type, _expected_pace(w.spec_json, w.vdot or vdot), log.avg_pace_sec_km, w.rpe)
    return {**check, "basis": "avg"} if check else None


def workout_view(w: Workout, lang: str, vdot: float, detail: bool = False,
                 log: Optional[ActivityLog] = None) -> Dict[str, Any]:
    """Session view. The list view passes an already-queried `log`; the detail view reads it from the session."""
    r = render(json.loads(w.spec_json), w.vdot or vdot, lang)
    if detail:
        log = w.activity_log
    check = session_pace_check(w, log, vdot)

    view = {
        "id": w.id,
        "week_number": w.week_number,
        "date": w.scheduled_date.isoformat(),
        "type": w.session_type,
        "title": r["title"],
        "distance_km": r["distance_km"],
        "duration_min": r["duration_min"],
        "status": w.status,
        "on_watch": bool(w.garmin_workout_id),
        "rpe": w.rpe,
        "pace": check["level"] if check else None,
        "pace_dir": check["direction"] if check else None,
    }
    if detail:
        view["description"] = r["description"]
        view["steps"] = r["steps"]
        if log:
            view["actual"] = {
                "distance_km": log.actual_distance_km,
                "duration_sec": log.actual_duration_sec,
                "pace_sec_km": log.avg_pace_sec_km,
                "avg_hr": log.avg_hr,
                "name": log.activity_name,
                "pace_check": check,
                "work": log_work(w, log),
            }
    return view


def new_workout(plan: TrainingPlan, s: Dict[str, Any], vdot: float) -> Workout:
    km, minutes = summarize(s["spec"], vdot)
    return Workout(
        plan_id=plan.id,
        week_number=s["week_number"],
        day_of_week=s["scheduled_date"].weekday(),
        scheduled_date=s["scheduled_date"],
        planned_date=s["scheduled_date"],
        session_type=s["session_type"],
        spec_json=json.dumps(s["spec"]),
        vdot=vdot,
        target_distance_km=km,
        estimated_duration_min=minutes,
        status="scheduled",
    )


def build_plan(plan: TrainingPlan) -> List[Dict[str, Any]]:
    factor, deloads = plan_adjustments(plan)
    return generate_plan(plan.target_distance, plan.start_date, plan.target_date, json.loads(plan.weekly_days),
                         plan.long_run_day, plan.terrain, plan.running_level, plan.injury_history,
                         volume_factor=factor, extra_deload_weeks=deloads, b_races=b_races(plan))


def regenerate_future(db: Session, plan: TrainingPlan) -> int:
    """Recomputes pending sessions from today with the plan's current adjustments and B races.
    Respects moved sessions (matched by their original date). If the session days change
    (when adding or removing a B race) it creates the missing ones and removes the extra ones;
    removed ones that were in Garmin go to the deletion queue."""
    today = date.today()
    by_date = {s["scheduled_date"]: s for s in build_plan(plan) if s["scheduled_date"] >= today}
    vdot = plan_vdot(plan)
    existing: Dict[date, Workout] = {}
    for w in db.query(Workout).filter(Workout.plan_id == plan.id):
        planned = w.planned_date or w.scheduled_date
        if planned >= today:
            existing[planned] = w
    changed = 0
    for planned, w in existing.items():
        if w.status != "scheduled" or w.scheduled_date < today:
            continue
        s = by_date.get(planned)
        if not s:
            _forget_garmin_ids(db, w)
            db.delete(w)
            changed += 1
            continue
        spec = json.dumps(s["spec"])
        if spec != w.spec_json:
            w.spec_json = spec
            w.session_type = s["session_type"]
            w.target_distance_km, w.estimated_duration_min = summarize(s["spec"], w.vdot or vdot)
            changed += 1
    for d, s in by_date.items():
        if d not in existing:
            db.add(new_workout(plan, s, vdot))
            changed += 1
    db.commit()
    return changed


# --- B races --------------------------------------------------------------------------

def is_b_race(w: Workout) -> bool:
    return w.session_type == "race" and json.loads(w.spec_json or "{}").get("priority") == "b"


def race_workout(db: Session, plan: TrainingPlan, race: PlanRace) -> Optional[Workout]:
    return db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.session_type == "race",
        Workout.planned_date == race.race_date,
    ).first()


def b_race_result(db: Session, plan: TrainingPlan, race: PlanRace) -> Optional[Dict[str, Any]]:
    """Time of a completed B race and the derived VDOT (None if there is no reliable data)."""
    w = race_workout(db, plan, race)
    log = w.activity_log if w and w.status == "completed" else None
    if not (log and log.actual_duration_sec and log.actual_distance_km):
        return None
    if log.actual_distance_km * 1000 < DISTANCE_METERS[race.distance] * B_RESULT_MIN_FRACTION:
        return None
    try:
        vdot = get_vdot_from_race(race.distance, log.actual_duration_sec)
    except ValueError:
        return None
    return {"time_sec": log.actual_duration_sec, "vdot": round(vdot, 1)}


def race_view(db: Session, plan: TrainingPlan, race: PlanRace) -> Dict[str, Any]:
    return {"id": race.id, "date": race.race_date.isoformat(), "distance": race.distance, "name": race.name,
            "result": b_race_result(db, plan, race) if race.race_date <= date.today() else None}


def b_race_proposal(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> Optional[Dict[str, Any]]:
    """Recent undecided B race whose time changes the plan's VDOT noticeably."""
    today = today or date.today()
    vdot = plan_vdot(plan)
    for race in reversed(plan.races):
        if race.vdot_decision or not 0 <= (today - race.race_date).days <= B_RESULT_DAYS:
            continue
        result = b_race_result(db, plan, race)
        if result and abs(result["vdot"] - vdot) >= B_RESULT_MIN_CHANGE:
            return {**race_view(db, plan, race), "vdot_from": round(vdot, 1), "vdot_to": result["vdot"]}
    return None


def unplanned_km_by_week(db: Session, plan: TrainingPlan) -> Dict[int, float]:
    """Km of activities recorded during the plan that did not match any session."""
    rows = db.query(ActivityLog.start_time, ActivityLog.actual_distance_km).filter(
        ActivityLog.user_id == plan.user_id,
        ActivityLog.workout_id.is_(None),
        ActivityLog.start_time >= datetime.combine(plan.start_date, datetime.min.time()),
        ActivityLog.start_time < datetime.combine(plan.target_date + timedelta(days=1), datetime.min.time()),
    ).all()
    km: Dict[int, float] = {}
    for start, dist in rows:
        n = week_of(plan.start_date, start.date())
        if 1 <= n <= plan.total_weeks:
            km[n] = km.get(n, 0.0) + (dist or 0)
    return km


def training_load(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> Dict[str, Any]:
    """Load (minutes × effort) and acute:chronic ratio of the plan's user.
    Counts all their recorded activities and sessions marked manually without an activity."""
    today = today or date.today()
    since = today - timedelta(days=56 + CHRONIC_DAYS)  # chart series + chronic window
    entries: List[Tuple[date, float]] = []
    logs = db.query(ActivityLog).filter(
        ActivityLog.user_id == plan.user_id,
        ActivityLog.start_time >= datetime.combine(since, datetime.min.time()),
    ).all()
    for log in logs:
        w = log.workout
        entries.append((log.start_time.date(), session_load(log.actual_duration_sec / 60, w.rpe if w else None,
                                                             w.session_type if w else None)))
    manual = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.status == "completed",
        Workout.scheduled_date >= since,
        ~Workout.activity_log.has(),
    ).all()
    for w in manual:
        entries.append((w.scheduled_date, session_load(w.estimated_duration_min or 0, w.rpe, w.session_type)))

    # History is reliable from the plan start, or earlier if activities were already recorded
    # (they are only recorded while a plan is active, so earlier gaps are not "zero").
    earliest = min((d for d, _ in entries if d >= plan.start_date - timedelta(days=CHRONIC_DAYS)), default=None)
    history_start = min(plan.start_date, earliest) if earliest else plan.start_date
    return load_status(entries, today, history_start)


@lru_cache(maxsize=1024)
def _session_vdot(spec_json: str, actual_sec_km: int, reference_vdot: float, work: bool) -> Optional[float]:
    return session_vdot(json.loads(spec_json), actual_sec_km, reference_vdot, work)


def form_view(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> Dict[str, Any]:
    """History of the current VDOT, estimated VDOT per quality session and current form."""
    today = today or date.today()
    vdot = plan_vdot(plan)
    rows = db.query(Workout, ActivityLog).join(ActivityLog, ActivityLog.workout_id == Workout.id).filter(
        Workout.plan_id == plan.id,
        Workout.status == "completed",
        Workout.session_type.in_(FORM_TYPES),
    ).order_by(Workout.scheduled_date).all()
    sessions = []
    for w, log in rows:
        work = log_work(w, log)
        actual = work_pace(work) if work else log.avg_pace_sec_km
        v = _session_vdot(w.spec_json, actual, round(w.vdot or vdot, 1), bool(work))
        if v:
            sessions.append({"date": log.start_time.date().isoformat(), "vdot": v, "type": w.session_type})

    history = db.query(VdotHistory).filter(VdotHistory.user_id == plan.user_id) \
        .order_by(VdotHistory.recorded_on, VdotHistory.id).all()
    # The last value before the plan is the starting point; if there is none, the first
    # (the VDOT the plan was created with) applies from the start
    before = [h for h in history if h.recorded_on <= plan.start_date]
    shown = ([before[-1]] if before else []) + [h for h in history if h.recorded_on > plan.start_date]
    steps = [{"date": (plan.start_date if i == 0 else h.recorded_on).isoformat(), "vdot": round(h.vdot, 1),
              "source": h.source} for i, h in enumerate(shown)]
    if not steps:
        steps = [{"date": plan.start_date.isoformat(), "vdot": round(vdot, 1), "source": "plan"}]

    estimate = form_estimate([(date.fromisoformat(s["date"]), s["vdot"]) for s in sessions], today)
    return {"vdot": round(vdot, 1), "history": steps, "sessions": sessions, "estimate": estimate}


@lru_cache(maxsize=512)
def _hard_fraction(spec_json: str, vdot: float) -> float:
    return hard_fraction(json.loads(spec_json), vdot)


def aerobic_view(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> Dict[str, Any]:
    """Aerobic efficiency of the plan's easy runs and intensity distribution over the last 4 weeks."""
    today = today or date.today()
    vdot = plan_vdot(plan)
    done = db.query(Workout).options(joinedload(Workout.activity_log)) \
        .filter(Workout.plan_id == plan.id, Workout.status == "completed").all()

    points = []
    for w in done:
        log = w.activity_log
        if w.session_type in EFFICIENCY_TYPES and log:
            v = meters_per_beat(log.actual_distance_km, log.actual_duration_sec, log.avg_hr)
            if v:
                points.append((log.start_time.date(), v))

    since = today - timedelta(days=INTENSITY_WINDOW_DAYS - 1)
    entries = []
    for w in done:
        log = w.activity_log
        day = log.start_time.date() if log else w.scheduled_date
        if not since <= day <= today:
            continue
        minutes = log.actual_duration_sec / 60 if log else (w.estimated_duration_min or 0)
        frac = _hard_fraction(w.spec_json, w.vdot or vdot)
        check = session_pace_check(w, log, vdot)
        too_fast = w.session_type in EFFICIENCY_TYPES and bool(check) and check["level"] == "off" \
            and check["direction"] == "fast"
        entries.append((minutes, frac, too_fast))
    # Activities outside the plan: assumed easy
    extra = db.query(ActivityLog.actual_duration_sec).filter(
        ActivityLog.user_id == plan.user_id,
        ActivityLog.workout_id.is_(None),
        ActivityLog.start_time >= datetime.combine(since, datetime.min.time()),
    ).all()
    entries += [(sec / 60, 0.0, False) for (sec,) in extra]

    return {"efficiency": efficiency_trend(points), "intensity": intensity_distribution(entries)}


# --- Statuses --------------------------------------------------------------------

def mark_missed(db: Session, plan: TrainingPlan) -> int:
    cutoff = date.today() - timedelta(days=MISSED_GRACE_DAYS)
    n = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.status == "scheduled",
        Workout.scheduled_date < cutoff,
    ).update({Workout.status: "missed"}, synchronize_session=False)
    if n:
        db.commit()
    return n


def move_workout(db: Session, w: Workout, new_date: date):
    plan = w.plan
    acct = account(plan)
    w.scheduled_date = new_date
    w.day_of_week = new_date.weekday()
    w.week_number = max(1, min(plan.total_weeks, week_of(plan.start_date, new_date)))
    if w.status == "missed" and new_date >= date.today():
        w.status = "scheduled"
    if w.garmin_workout_id and acct.is_connected():
        try:
            w.garmin_schedule_id = acct.reschedule(w.garmin_workout_id, w.garmin_schedule_id, new_date)
        except Exception as e:
            logger.warning(f"Could not move in Garmin, will re-upload: {e}")
            _forget_garmin_ids(db, w)
            db.commit()
            delete_pending(db, plan.user_id)
    db.commit()


def record_vdot(db: Session, user_id: int, vdot: float, source: str, plan_id: Optional[int] = None):
    """Records the current VDOT in the history (one entry per day; skipped if unchanged)."""
    today = date.today()
    last = db.query(VdotHistory).filter(VdotHistory.user_id == user_id) \
        .order_by(VdotHistory.recorded_on.desc(), VdotHistory.id.desc()).first()
    if last and last.recorded_on == today:
        last.vdot, last.source, last.plan_id = round(vdot, 1), source, plan_id or last.plan_id
    elif not last or abs(last.vdot - vdot) >= 0.05:
        db.add(VdotHistory(user_id=user_id, plan_id=plan_id, recorded_on=today, vdot=round(vdot, 1), source=source))
    db.commit()


def set_plan_vdot(db: Session, plan: TrainingPlan, vdot: float, source: str = "reference"):
    """Applies a new VDOT to pending sessions from today and records it in the history."""
    record_vdot(db, plan.user_id, vdot, source, plan.id)
    plan.vdot = vdot
    db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.status == "scheduled",
        Workout.scheduled_date >= date.today(),
    ).update({Workout.vdot: vdot}, synchronize_session=False)
    db.commit()


# --- Garmin -------------------------------------------------------------------------

def _forget_garmin_ids(db: Session, w: Workout):
    """Moves the session's Garmin ids to the deletion queue and clears them from the session.
    They are not lost until Garmin confirms the deletion."""
    if w.garmin_workout_id or w.garmin_schedule_id:
        db.add(GarminDeletion(user_id=w.plan.user_id, garmin_workout_id=w.garmin_workout_id,
                              garmin_schedule_id=w.garmin_schedule_id))
    w.garmin_workout_id = None
    w.garmin_schedule_id = None


def pending_deletions(db: Session, user_id: int) -> int:
    return db.query(GarminDeletion).filter(GarminDeletion.user_id == user_id).count()


def delete_pending(db: Session, user_id: int) -> Dict[str, int]:
    """Deletes queued workouts in Garmin. Failed ones are left for the next cycle."""
    rows = db.query(GarminDeletion).filter(
        GarminDeletion.user_id == user_id,
        GarminDeletion.attempts < MAX_DELETE_ATTEMPTS,
    ).order_by(GarminDeletion.id).all()
    acct = garmin_accounts.get(user_id)
    if not rows or not acct.is_connected():
        return {"deleted": 0, "failed": 0}
    deleted = failed = 0
    with _sync_lock:
        for r in rows:
            if acct.delete_workout(r.garmin_workout_id, r.garmin_schedule_id):
                db.delete(r)
                deleted += 1
            else:
                r.attempts += 1
                r.last_error = f"attempt {r.attempts} failed {datetime.now():%Y-%m-%d %H:%M}"
                failed += 1
            db.commit()
            time.sleep(0.2)
    if failed:
        logger.error(f"User {user_id}: {failed} workouts could not be deleted from Garmin; will retry")
    return {"deleted": deleted, "failed": failed}


def sync_window(db: Session, plan: TrainingPlan) -> Dict[str, int]:
    """Uploads pending sessions in the rolling window to Garmin."""
    sync_status.start(plan.user_id)
    result = None
    try:
        result = _sync_window(db, plan)
        return result
    finally:
        sync_status.finish(plan.user_id, result["errors"] if result else 1)


def _sync_window(db: Session, plan: TrainingPlan) -> Dict[str, int]:
    acct = account(plan)
    if not acct.is_connected():
        return {"synced": 0, "errors": 0}
    today = date.today()
    lang, vdot = language(plan), plan_vdot(plan)
    pending = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.status == "scheduled",
        Workout.garmin_workout_id.is_(None),
        Workout.scheduled_date >= today,
        Workout.scheduled_date <= today + timedelta(days=SYNC_WINDOW_DAYS),
    ).order_by(Workout.scheduled_date).all()
    synced = errors = 0
    with _sync_lock:
        for w in pending:
            # The plan may have been cancelled (or the session moved) while earlier ones were uploading
            db.refresh(plan)
            db.refresh(w)
            if plan.status != "active" or w.status != "scheduled" or w.garmin_workout_id:
                continue
            try:
                payload = garmin_payload(json.loads(w.spec_json), w.vdot or vdot, lang)
                w.garmin_workout_id, w.garmin_schedule_id = acct.upload_and_schedule(payload, w.scheduled_date)
                db.commit()
                synced += 1
            except Exception as e:
                db.rollback()
                errors += 1
                logger.error(f"Error uploading session {w.id} to Garmin: {e}")
    # If cancelled during the upload, the just-uploaded sessions are removed too
    db.refresh(plan)
    if synced and plan.status != "active":
        unsync_future(db, plan)
        delete_pending(db, plan.user_id)
    return {"synced": synced, "errors": errors}


def unsync_future(db: Session, plan: TrainingPlan) -> int:
    """Moves future non-completed sessions that are in Garmin to the deletion queue."""
    rows = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.status != "completed",
        Workout.garmin_workout_id.isnot(None),
        Workout.scheduled_date >= date.today(),
    ).all()
    for w in rows:
        _forget_garmin_ids(db, w)
    db.commit()
    return len(rows)


def delete_from_garmin(user_id: int):
    """For BackgroundTasks: processes the user's deletion queue."""
    db = SessionLocal()
    try:
        delete_pending(db, user_id)
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting Garmin workouts for user {user_id}: {e}")
    finally:
        db.close()


def is_finished(db: Session, plan: TrainingPlan) -> bool:
    """Race day has arrived or the plan's last session is completed."""
    if date.today() >= plan.target_date:
        return True
    last = db.query(Workout).filter(Workout.plan_id == plan.id) \
        .order_by(Workout.scheduled_date.desc(), Workout.id.desc()).first()
    return bool(last and last.status == "completed")


def close_plan(db: Session, plan: TrainingPlan) -> int:
    """Closes the plan: "completed" if it is over (is_finished), otherwise "cancelled".
    Queues its pending sessions for deletion in Garmin and returns how many."""
    finished = is_finished(db, plan)
    queued = unsync_future(db, plan)
    db.query(Workout).filter(Workout.plan_id == plan.id, Workout.status == "scheduled") \
        .update({Workout.status: "missed"}, synchronize_session=False)
    plan.status = "completed" if finished else "cancelled"
    db.commit()
    return queued


def finish_if_over(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> bool:
    """Closes as completed a plan whose race was FINISH_AFTER_DAYS or more days ago."""
    if plan.status != "active" or (today or date.today()) < plan.target_date + timedelta(days=FINISH_AFTER_DAYS):
        return False
    close_plan(db, plan)
    logger.info(f"Plan {plan.id} completed")
    return True


# --- Activity reconciliation --------------------------------------------------------

def parse_activity(act: Dict[str, Any]) -> Dict[str, Any]:
    start_str = act.get("startTimeLocal") or ""
    start = datetime.fromisoformat(start_str.replace("T", " ")) if start_str else datetime.now()
    distance_km = round((act.get("distance") or 0) / 1000.0, 2)
    duration = int(act.get("duration") or 0)
    pace = int(round(duration / distance_km)) if distance_km > 0 else 0
    return {
        "garmin_activity_id": str(act.get("activityId")),
        "start_time": start,
        "activity_name": act.get("activityName") or "Run",
        "actual_distance_km": distance_km,
        "actual_duration_sec": duration,
        "avg_pace_sec_km": pace,
        "avg_hr": int(act["averageHR"]) if act.get("averageHR") else None,
        "max_hr": int(act["maxHR"]) if act.get("maxHR") else None,
        "calories": int(act["calories"]) if act.get("calories") else None,
    }


def match_workout(candidates: List[Workout], day: date, distance_km: float = 0,
                  busy_days: Set[date] = frozenset()) -> Optional[Workout]:
    """The non-completed session closest to the date (±1 day), preferring the same day and then the previous one.
    An activity does not pull forward the next day's session if that day already had its own (busy_days: e.g. a
    second easy run), nor completes a session it covers less than half of (a loose jog, a warm-up)."""
    def fits(w: Workout) -> bool:
        gap = (w.scheduled_date - day).days
        if abs(gap) > MATCH_TOLERANCE_DAYS or (gap > 0 and day in busy_days):
            return False
        planned = w.target_distance_km
        return not (distance_km and planned and distance_km < planned * MATCH_MIN_FRACTION)

    close = [w for w in candidates if fits(w)]
    if not close:
        return None
    return min(close, key=lambda w: (abs((w.scheduled_date - day).days), w.scheduled_date > day))


def reconcile_activities(db: Session, plan: TrainingPlan) -> int:
    today = date.today()
    acts = account(plan).get_running_activities(today - timedelta(days=10), today)
    ids = [str(a.get("activityId")) for a in acts]
    known = {a for (a,) in db.query(ActivityLog.garmin_activity_id).filter(ActivityLog.garmin_activity_id.in_(ids))}
    busy_days = {d for (d,) in db.query(Workout.scheduled_date).filter(Workout.plan_id == plan.id)}
    matched = 0
    for act in sorted(acts, key=lambda a: a.get("startTimeLocal") or ""):
        data = parse_activity(act)
        if data["garmin_activity_id"] in known:
            continue
        candidates = db.query(Workout).filter(
            Workout.plan_id == plan.id,
            Workout.status.in_(["scheduled", "missed"]),
        ).all()
        w = match_workout(candidates, data["start_time"].date(), data["actual_distance_km"], busy_days)
        if w:
            w.status = "completed"
            matched += 1
        db.add(ActivityLog(user_id=plan.user_id, workout_id=w.id if w else None, **data))
        db.commit()
        known.add(data["garmin_activity_id"])
    return matched


def fetch_missing_laps(db: Session, plan: TrainingPlan, limit: int = LAPS_PER_CYCLE) -> int:
    """Reads from Garmin the laps of completed tempos and intervals that do not have them yet."""
    acct = account(plan)
    if not acct.is_connected():
        return 0
    logs = db.query(ActivityLog).join(Workout, ActivityLog.workout_id == Workout.id).filter(
        Workout.plan_id == plan.id,
        Workout.session_type.in_(WORK_KINDS),
        ActivityLog.laps_json.is_(None),
    ).order_by(ActivityLog.start_time.desc()).limit(limit).all()
    fetched = 0
    for log in logs:
        try:
            laps = acct.get_laps(log.garmin_activity_id)
        except Exception as e:
            logger.warning(f"Could not read laps for activity {log.garmin_activity_id}: {e}")
            continue  # retried in the next cycle
        log.laps_json = json.dumps(laps or [])
        db.commit()
        fetched += 1
        time.sleep(0.2)
    return fetched


# --- History -----------------------------------------------------------------------------

def plan_summary(db: Session, plan: TrainingPlan) -> Dict[str, Any]:
    """Plan summary for the history: compliance, VDOT progression and race."""
    vdot_end = plan_vdot(plan)
    first = db.query(VdotHistory).filter(VdotHistory.plan_id == plan.id) \
        .order_by(VdotHistory.recorded_on, VdotHistory.id).first()
    vdot_start = first.vdot if first else vdot_end
    workouts = db.query(Workout).options(joinedload(Workout.activity_log)).filter(Workout.plan_id == plan.id).all()
    sessions, race = [], None
    for w in workouts:
        log = w.activity_log
        check = session_pace_check(w, log, vdot_end)
        sessions.append({"type": w.session_type, "status": w.status, "planned_km": w.target_distance_km,
                         "actual_km": log.actual_distance_km if log else None,
                         "pace": check["level"] if check else None})
        if w.session_type == "race" and not is_b_race(w) and w.status == "completed" and log:
            race = {"date": log.start_time.date().isoformat(), "time_sec": log.actual_duration_sec,
                    "distance_km": log.actual_distance_km, "pace_sec_km": log.avg_pace_sec_km}
    predicted = predict_race_time_range(vdot_end, plan.target_distance, plan.terrain)
    return {
        "id": plan.id,
        "name": plan.name,
        "status": plan.status,
        "target_distance": plan.target_distance,
        "target_date": plan.target_date.isoformat(),
        "start_date": plan.start_date.isoformat(),
        "total_weeks": plan.total_weeks,
        "vdot_start": round(vdot_start, 1),
        "vdot_end": round(vdot_end, 1),
        "predicted_sec": predicted["nominal_sec"],
        "race": race,
        "reviews_accepted": sum(1 for r in plan.reviews if r.decision == "accepted"),
        "adherence": adherence(sessions),
    }


def plan_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Closed plans, newest first. Cancelled plans with no
    completed session are skipped (redone or mistakenly created plans)."""
    plans = db.query(TrainingPlan).filter(TrainingPlan.user_id == user_id, TrainingPlan.status != "active") \
        .order_by(TrainingPlan.target_date.desc(), TrainingPlan.id.desc()).all()
    out = []
    for plan in plans:
        s = plan_summary(db, plan)
        if plan.status == "completed" or s["adherence"]["sessions"]["done"]:
            out.append(s)
    return out


# --- Tasks ----------------------------------------------------------------------------

def run_cycle_for_user(db: Session, user_id: int):
    if not garmin_accounts.get(user_id).is_connected():
        return
    try:
        delete_pending(db, user_id)  # deletion retries, with or without an active plan
    except Exception as e:
        db.rollback()
        logger.warning(f"Could not process deletion queue for user {user_id}: {e}")
    plan = get_active_plan(db, user_id)
    if not plan:
        return
    try:
        reconcile_activities(db, plan)
        fetch_missing_laps(db, plan)
    except Exception as e:
        db.rollback()
        logger.warning(f"Could not reconcile activities for user {user_id}: {e}")
    if finish_if_over(db, plan):
        return
    mark_missed(db, plan)
    sync_window(db, plan)


def run_cycle(user_id: Optional[int] = None):
    """Periodic task: reconcile activities, mark missed sessions and sync the window.
    Without user_id it iterates over all users with a Garmin account."""
    db = SessionLocal()
    try:
        ids = [user_id] if user_id else [u for (u,) in db.query(UserProfile.id).filter(UserProfile.garmin_user_id.isnot(None))]
        for uid in ids:
            try:
                run_cycle_for_user(db, uid)
            except Exception as e:
                db.rollback()
                logger.error(f"Error in cycle for user {uid}: {e}")
    finally:
        db.close()
    try:
        checkpoint()
    except Exception as e:
        logger.warning(f"Could not checkpoint the database: {e}")


def sync_user(user_id: int):
    """For BackgroundTasks: uploads the window of the user's active plan."""
    db = SessionLocal()
    try:
        plan = get_active_plan(db, user_id)
        if plan:
            sync_window(db, plan)
    except Exception as e:
        logger.error(f"Error syncing user {user_id}: {e}")
    finally:
        sync_status.finish(user_id)
        db.close()


def resync_user(user_id: int):
    """Re-uploads the active plan's window (after a VDOT, language or settings change)."""
    db = SessionLocal()
    try:
        plan = get_active_plan(db, user_id)
        if not plan:
            return
        unsync_future(db, plan)
        delete_pending(db, user_id)
        sync_window(db, plan)
    except Exception as e:
        logger.error(f"Error re-syncing user {user_id}: {e}")
    finally:
        sync_status.finish(user_id)
        db.close()
