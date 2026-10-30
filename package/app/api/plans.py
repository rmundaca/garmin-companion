import json
import logging
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.profile import set_reference
from app.core.database import get_db
from app.core.security import current_user
from app.engine.periodization import (
    MAX_WEEKS, MIN_WEEKS, b_race_error, count_weeks, generate_plan, get_duration_recommendation,
)
from app.engine.stats import adherence
from app.engine.vdot import get_vdot_from_race, predict_race_time_range
from app.models.schemas import ActivityLog, PlanRace, PlanReview, TrainingPlan, UserProfile, Workout
from app.services import plan_service, review_service

router = APIRouter(prefix="/api/plans", tags=["plans"])
logger = logging.getLogger("api_plans")

DISTANCES = ("5k", "10k", "21k", "42k")
TERRAINS = ("flat", "rolling", "moderate", "hilly")
LEVELS = ("beginner", "intermediate", "advanced", "elite")
INJURIES = ("rarely_never", "minor_past", "frequent_recent")
RPE_PROMPT_DAYS = 3


class PlanParams(BaseModel):
    target_distance: str
    target_date: date
    start_date: Optional[date] = None
    running_level: str = "intermediate"
    injury_history: str = "rarely_never"
    terrain: str = "flat"
    reference_distance: Optional[str] = None
    reference_time_sec: Optional[int] = None


class PlanCreate(PlanParams):
    weekly_days: List[int]  # 0=Monday ... 6=Sunday
    long_run_day: int
    name: Optional[str] = None


class ReviewAnswers(BaseModel):
    fatigue: Optional[str] = None
    pain: Optional[str] = None
    skip: bool = False


class ReviewDecision(BaseModel):
    accept: bool


class RaceCreate(BaseModel):
    race_date: date
    distance: str
    name: Optional[str] = None


def _default_start() -> date:
    today = date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)  # next Monday


def _validate(req: PlanParams) -> date:
    if req.target_distance not in DISTANCES or req.terrain not in TERRAINS \
            or req.running_level not in LEVELS or req.injury_history not in INJURIES:
        raise HTTPException(status_code=400, detail="invalid_params")
    start = req.start_date or _default_start()
    if start < date.today():
        raise HTTPException(status_code=400, detail="start_in_past")
    weeks = count_weeks(start, req.target_date)
    if req.target_date <= start or weeks < MIN_WEEKS:
        raise HTTPException(status_code=400, detail="plan_too_short")
    if weeks > MAX_WEEKS:
        raise HTTPException(status_code=400, detail="plan_too_long")
    return start


def _predictions(vdot: float, form_vdot: Optional[float], target: str, terrain: str) -> List[dict]:
    """Predicted time at each distance with the plan VDOT and with the estimated fitness.
    The target distance uses the plan's elevation; the rest, flat."""
    rows = []
    for d in DISTANCES:
        t = terrain if d == target else "flat"
        rows.append({
            "distance": d,
            "is_target": d == target,
            "plan": predict_race_time_range(vdot, d, t)["formatted_nominal"],
            "form": predict_race_time_range(form_vdot, d, t)["formatted_nominal"] if form_vdot else None,
        })
    return rows


def _active_or_404(db: Session, user: UserProfile) -> TrainingPlan:
    plan = plan_service.get_active_plan(db, user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="no_active_plan")
    return plan


@router.post("/preview")
def preview_plan(req: PlanParams, user: UserProfile = Depends(current_user)):
    """Data for the wizard: weeks, recommendation and prediction. Saves nothing."""
    start = req.start_date or _default_start()
    vdot = user.calculated_vdot
    if req.reference_distance and req.reference_time_sec:
        try:
            vdot = get_vdot_from_race(req.reference_distance, req.reference_time_sec)
        except ValueError:
            raise HTTPException(status_code=400, detail="invalid_time")
    return {
        "start_date": start.isoformat(),
        "weeks": count_weeks(start, req.target_date) if req.target_date > start else 0,
        "recommendation": get_duration_recommendation(req.target_distance, req.running_level, req.injury_history),
        "vdot": round(vdot, 1),
        "prediction": predict_race_time_range(vdot, req.target_distance, req.terrain),
    }


@router.post("")
def create_plan(req: PlanCreate, background: BackgroundTasks,
                user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    start = _validate(req)
    days = sorted({d for d in req.weekly_days if 0 <= d <= 6})
    if len(days) < 2 or not 0 <= req.long_run_day <= 6:
        raise HTTPException(status_code=400, detail="invalid_days")

    if req.reference_distance and req.reference_time_sec:
        set_reference(db, user, req.reference_distance, req.reference_time_sec)
    vdot = user.calculated_vdot

    previous = plan_service.get_active_plan(db, user.id)
    if previous:
        plan_service.close_plan(db, previous)

    distance = req.target_distance
    prediction = predict_race_time_range(vdot, distance, req.terrain)
    plan = TrainingPlan(
        user_id=user.id,
        name=((req.name or "").strip() or f"{distance.upper()} · {req.target_date.strftime('%d/%m/%Y')}")[:80],
        target_distance=distance,
        target_date=req.target_date,
        start_date=start,
        total_weeks=count_weeks(start, req.target_date),
        weekly_days=json.dumps(days),
        long_run_day=req.long_run_day,
        terrain=req.terrain,
        running_level=req.running_level,
        injury_history=req.injury_history,
        vdot=vdot,
        predicted_time_min_sec=prediction["min_sec"],
        predicted_time_max_sec=prediction["max_sec"],
        status="active",
    )
    db.add(plan)
    db.flush()
    for s in generate_plan(distance, start, req.target_date, days, req.long_run_day,
                           req.terrain, req.running_level, req.injury_history):
        db.add(plan_service.new_workout(plan, s, vdot))
    db.commit()
    plan_service.record_vdot(db, user.id, vdot, "plan", plan.id)

    # First remove the previous plan's sessions from Garmin, then upload the new one
    plan_service.sync_status.start(user.id)
    background.add_task(plan_service.delete_from_garmin, user.id)
    background.add_task(plan_service.sync_user, user.id)
    return {"plan_id": plan.id, "weeks": plan.total_weeks}


def _workout_views(db: Session, plan: TrainingPlan, lang: str, vdot: float):
    """Plan sessions by date, their logged activity (by session id) and their list view."""
    workouts = db.query(Workout).filter(Workout.plan_id == plan.id) \
        .order_by(Workout.scheduled_date, Workout.id).all()
    logs = {log.workout_id: log for log in
            db.query(ActivityLog).filter(ActivityLog.workout_id.in_([w.id for w in workouts]))}
    return workouts, logs, [plan_service.workout_view(w, lang, vdot, log=logs.get(w.id)) for w in workouts]


@router.get("/active")
def active_plan(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Everything the Today and Plan tabs need in a single response (Progress is separate)."""
    plan = plan_service.get_active_plan(db, user.id)
    if not plan or plan_service.finish_if_over(db, plan):
        return {"active": False}

    plan_service.mark_missed(db, plan)
    lang, vdot = plan_service.language(plan), plan_service.plan_vdot(plan)
    today = date.today()
    week_now = plan_service.current_week(plan, today)

    workouts, logs, views = _workout_views(db, plan, lang, vdot)
    actual_km = {wid: log.actual_distance_km for wid, log in logs.items()}

    extra_km = plan_service.unplanned_km_by_week(db, plan)
    weeks = [{"week_number": i, "phase": ph, "planned_km": 0.0, "done_km": 0.0,
              "extra_km": round(extra_km.get(i, 0.0), 1), "is_current": i == week_now, "workouts": []}
             for i, ph in enumerate(plan_service.phases_for(plan), start=1)]
    for v in views:
        wk = weeks[min(len(weeks), max(1, v["week_number"])) - 1]
        wk["workouts"].append(v)
        wk["planned_km"] += v["distance_km"] or 0
        if v["status"] == "completed":
            wk["done_km"] += actual_km.get(v["id"], v["distance_km"] or 0)
    for wk in weeks:
        wk["planned_km"] = round(wk["planned_km"], 1)
        wk["done_km"] = round(wk["done_km"], 1)

    done = sum(1 for v in views if v["status"] == "completed")
    missed = sum(1 for v in views if v["status"] == "missed")
    upcoming = [v for v in views if v["status"] == "scheduled" and v["date"] >= today.isoformat()]
    window_end = (today + timedelta(days=plan_service.SYNC_WINDOW_DAYS)).isoformat()
    in_window = [v for v in upcoming if v["date"] <= window_end]
    soon = (today + timedelta(days=1)).isoformat()
    by_id = {w.id: w for w in workouts}

    next_workout = None
    if upcoming:
        next_workout = plan_service.workout_view(by_id[upcoming[0]["id"]], lang, vdot, detail=True)

    rpe_cutoff = (today - timedelta(days=RPE_PROMPT_DAYS)).isoformat()
    rpe_prompt = next((v for v in reversed(views)
                       if v["status"] == "completed" and not v["rpe"] and rpe_cutoff <= v["date"] <= today.isoformat()), None)
    factor, _ = plan_service.plan_adjustments(plan)

    return {
        "active": True,
        "plan": {
            "id": plan.id,
            "name": plan.name,
            "target_distance": plan.target_distance,
            "target_date": plan.target_date.isoformat(),
            "start_date": plan.start_date.isoformat(),
            "total_weeks": plan.total_weeks,
            "current_week": week_now,
            "days_to_race": max(0, (plan.target_date - today).days),
            "terrain": plan.terrain,
            "running_level": plan.running_level,
            "injury_history": plan.injury_history,
            "weekly_days": json.loads(plan.weekly_days),
            "long_run_day": plan.long_run_day,
            "vdot": round(vdot, 1),
            "volume_factor": factor,
            "finished": plan_service.is_finished(db, plan),
        },
        "races": [plan_service.race_view(db, plan, r) for r in plan.races],
        "race_proposal": plan_service.b_race_proposal(db, plan, today),
        "prediction": predict_race_time_range(vdot, plan.target_distance, plan.terrain),
        "stats": {
            "sessions_done": done,
            "sessions_total": len(views),
            "compliance": round(100 * done / (done + missed)) if done + missed else None,
            "km_done": round(sum(w["done_km"] for w in weeks), 1),
            "km_planned": round(sum(w["planned_km"] for w in weeks), 1),
        },
        "next_workout": next_workout,
        "rpe_prompt": rpe_prompt,
        "review": review_service.review_state(db, plan),
        "weeks": weeks,
        "sync": {
            "connected": plan_service.account(plan).is_connected(),
            "window_days": plan_service.SYNC_WINDOW_DAYS,
            "pending": sum(1 for v in in_window if not v["on_watch"]),
            "on_watch": sum(1 for v in in_window if v["on_watch"]),
            # Only today and tomorrow are urgent: the hourly cycle uploads the rest
            "pending_soon": sum(1 for v in in_window if not v["on_watch"] and v["date"] <= soon),
            "syncing": plan_service.sync_status.syncing(user.id),
            "failed": plan_service.sync_status.failed(user.id),
        },
    }


@router.get("/history")
def history(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    return {"plans": plan_service.plan_history(db, user.id)}


@router.get("/active/progress")
def progress(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Progress tab. Separate because it is the most expensive to compute: requested only when opened."""
    plan = _active_or_404(db, user)
    lang, vdot = plan_service.language(plan), plan_service.plan_vdot(plan)
    today = date.today()
    _, logs, views = _workout_views(db, plan, lang, vdot)
    form = plan_service.form_view(db, plan, today)
    form["predictions"] = _predictions(vdot, (form["estimate"] or {}).get("vdot"), plan.target_distance, plan.terrain)
    acct = plan_service.account(plan)
    return {
        "form": form,
        "load": plan_service.training_load(db, plan, today),
        **plan_service.aerobic_view(db, plan, today),
        "adherence": adherence([{"type": v["type"], "status": v["status"], "planned_km": v["distance_km"],
                                 "actual_km": logs[v["id"]].actual_distance_km if v["id"] in logs else None,
                                 "pace": v["pace"]} for v in views]),
        "vo2max": acct.get_recent_vo2max() if acct.is_connected() else None,
    }


@router.post("/active/review")
def answer_review(req: ReviewAnswers, user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    if not req.skip and (req.fatigue not in review_service.FATIGUE or req.pain not in review_service.PAIN):
        raise HTTPException(status_code=400, detail="invalid_params")
    plan = _active_or_404(db, user)
    if any(r.decision == "pending" for r in plan.reviews):
        raise HTTPException(status_code=409, detail="review_pending")
    review = review_service.create_review(db, plan, req.fatigue, req.pain, req.skip)
    if not review:
        raise HTTPException(status_code=409, detail="no_review_due")
    db.refresh(plan)
    return review_service.review_state(db, plan) or {"stage": "done"}


@router.post("/active/review/{review_id}")
def decide_review(review_id: int, req: ReviewDecision, background: BackgroundTasks,
                  user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    plan = _active_or_404(db, user)
    review = db.query(PlanReview).filter(PlanReview.id == review_id, PlanReview.plan_id == plan.id).first()
    if not review or review.decision != "pending":
        raise HTTPException(status_code=404, detail="review_not_found")
    if review_service.decide(db, plan, review, req.accept):
        plan_service.sync_status.start(user.id)
        background.add_task(plan_service.resync_user, user.id)
    return {"decision": review.decision}


def _replan(db: Session, plan: TrainingPlan, user: UserProfile, background: BackgroundTasks):
    """Rebuilds future sessions after B races change and re-uploads the window."""
    db.refresh(plan)
    plan_service.regenerate_future(db, plan)
    plan_service.sync_status.start(user.id)
    background.add_task(plan_service.resync_user, user.id)


@router.post("/active/races")
def add_race(req: RaceCreate, background: BackgroundTasks,
             user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Adds a B race: the plan adjusts around it (taper and recovery)."""
    plan = _active_or_404(db, user)
    if req.race_date <= date.today():
        raise HTTPException(status_code=400, detail="b_race_in_past")
    error = b_race_error(plan.start_date, plan.target_date, plan.target_distance, req.race_date,
                         req.distance, [r.race_date for r in plan.races])
    if error:
        raise HTTPException(status_code=400, detail=error)
    db.add(PlanRace(plan_id=plan.id, race_date=req.race_date, distance=req.distance,
                    name=(req.name or "").strip()[:80] or None))
    db.commit()
    _replan(db, plan, user, background)
    return {"races": [plan_service.race_view(db, plan, r) for r in plan.races]}


@router.delete("/active/races/{race_id}")
def delete_race(race_id: int, background: BackgroundTasks,
                user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    plan = _active_or_404(db, user)
    race = db.query(PlanRace).filter(PlanRace.id == race_id, PlanRace.plan_id == plan.id).first()
    if not race:
        raise HTTPException(status_code=404, detail="race_not_found")
    if race.race_date <= date.today():
        raise HTTPException(status_code=409, detail="b_race_in_past")
    db.delete(race)
    db.commit()
    _replan(db, plan, user, background)
    return {"races": [plan_service.race_view(db, plan, r) for r in plan.races]}


@router.post("/active/races/{race_id}/vdot")
def decide_race_vdot(race_id: int, req: ReviewDecision, background: BackgroundTasks,
                     user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Applies (or dismisses) the VDOT derived from a B race time. When applied, the race
    also becomes the profile's reference time."""
    plan = _active_or_404(db, user)
    race = db.query(PlanRace).filter(PlanRace.id == race_id, PlanRace.plan_id == plan.id).first()
    if not race or race.vdot_decision:
        raise HTTPException(status_code=404, detail="race_not_found")
    result = plan_service.b_race_result(db, plan, race) if req.accept else None
    if req.accept and not result:
        raise HTTPException(status_code=409, detail="no_race_result")
    race.vdot_decision = "applied" if req.accept else "dismissed"
    db.commit()
    if result:
        set_reference(db, user, race.distance, result["time_sec"])
        plan_service.set_plan_vdot(db, plan, user.calculated_vdot, "race_b")
        plan_service.sync_status.start(user.id)
        background.add_task(plan_service.resync_user, user.id)
    return {"decision": race.vdot_decision, "vdot": round(plan_service.plan_vdot(plan), 1)}


@router.post("/active/sync")
def sync_active(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Imports pending activities from Garmin and uploads the session window to the watch."""
    plan = _active_or_404(db, user)
    if not plan_service.account(plan).is_connected():
        raise HTTPException(status_code=400, detail="garmin_not_connected")
    try:
        imported = plan_service.reconcile_activities(db, plan)
    except Exception as e:
        db.rollback()
        logger.warning(f"Could not import activities for user {user.id}: {e}")
        imported = None
    plan_service.mark_missed(db, plan)
    result = plan_service.sync_window(db, plan)
    return {**result, "imported": imported}


@router.post("/{plan_id}/cancel")
def cancel(plan_id: int, background: BackgroundTasks,
           user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    plan = db.query(TrainingPlan).filter(TrainingPlan.id == plan_id, TrainingPlan.user_id == user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="plan_not_found")
    plan_service.close_plan(db, plan)
    background.add_task(plan_service.delete_from_garmin, user.id)
    return {"status": plan.status}
