"""
Periodic plan review (every REVIEW_EVERY_WEEKS weeks).

1. Period metrics: compliance, km, actual vs expected pace deviation, RPE and
   acute:chronic load ratio (ACWR).
2. Two questions for the user: fatigue and pain.
3. Deterministic, explainable rules → proposal (VDOT, volume factor, deload).
4. If accepted: it is applied to the plan, future sessions are regenerated and re-synced.

Limits: volume never rises above the original plan (factor ≤ 1) nor drops below 0.7;
VDOT changes by at most ±1 per review.
"""
import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.engine.periodization import week_of
from app.engine.stats import ACWR_HIGH, ACWR_SPIKE, EASY_COMFORT_RPE
from app.engine.vdot import predict_race_time_range
from app.models.schemas import PlanReview, TrainingPlan, Workout
from app.services import plan_service

FATIGUE = ("good", "tired", "very_tired")
PAIN = ("no", "mild", "yes")
QUALITY = ("tempo", "intervals")
EASY = ("easy", "long_run")
REVIEW_EVERY_WEEKS = 2
MIN_FACTOR, MAX_FACTOR = 0.7, 1.0
FORM_GAP_TIP = 1.5
QUALITY_SLOW = -0.03  # quality sessions slower than planned pace (outside the "ok" range)
FADE_TIP = 0.03  # the last reps are 3 % or more slower than the first
EFFICIENCY_TIP = 3.0  # % change in aerobic efficiency worth a comment


# --- Review due? -----------------------------------------------------------------

def due_period(db: Session, plan: TrainingPlan, today: Optional[date] = None) -> Optional[Tuple[int, int]]:
    """(week_from, week_to) to review, or None. Only full weeks are reviewed."""
    today = today or date.today()
    every = REVIEW_EVERY_WEEKS
    week_now = week_of(plan.start_date, today)
    if week_now >= plan.total_weeks:  # race week: no more adjustments
        return None
    last_full = week_now - 1
    last_reviewed = max((r.week_to for r in plan.reviews), default=0)
    if last_full >= every and last_full - last_reviewed >= every:
        return last_full - every + 1, last_full
    return None


# --- Metrics -----------------------------------------------------------------------

def _mean(values: List[float]) -> Optional[float]:
    return sum(values) / len(values) if values else None


def compute_metrics(db: Session, plan: TrainingPlan, week_from: int, week_to: int) -> Dict[str, Any]:
    rows = db.query(Workout).filter(
        Workout.plan_id == plan.id,
        Workout.week_number >= week_from,
        Workout.week_number <= week_to,
        Workout.session_type != "race",
    ).all()
    vdot = plan_service.plan_vdot(plan)
    done = [w for w in rows if w.status == "completed"]
    quality_dev, easy_dev, easy_rpe, fades = [], [], [], []
    km_done = 0.0
    for w in done:
        log = w.activity_log
        km_done += log.actual_distance_km if log else (w.target_distance_km or 0)
        # Tempo and intervals: work blocks if Garmin recorded the laps, otherwise the average pace
        check = plan_service.session_pace_check(w, log, vdot)
        if not check:
            continue
        deviation = check["deviation"]  # > 0: faster than planned
        (quality_dev if w.session_type in QUALITY else easy_dev if w.session_type in EASY else []).append(deviation)
        if w.session_type in EASY and w.rpe:
            easy_rpe.append(w.rpe)
        work = plan_service.log_work(w, log)
        if work and work["fade"] is not None:
            fades.append(work["fade"])
    rpes = [w.rpe for w in done if w.rpe]
    return {
        "planned": len(rows),
        "completed": len(done),
        "compliance": round(len(done) / len(rows), 2) if rows else None,
        "km_planned": round(sum(w.target_distance_km or 0 for w in rows), 1),
        "km_done": round(km_done, 1),
        "quality_dev": round(_mean(quality_dev), 3) if len(quality_dev) >= 2 else None,
        "quality_count": len(quality_dev),
        # Mean even with a single session: not enough to move the VDOT, but enough to qualify a tip
        "quality_mean": round(_mean(quality_dev), 3) if quality_dev else None,
        "easy_dev": round(_mean(easy_dev), 3) if len(easy_dev) >= 2 else None,
        "easy_rpe": round(_mean(easy_rpe), 1) if easy_rpe else None,
        "fade": round(_mean(fades), 3) if fades else None,
        "rpe_avg": round(_mean(rpes), 1) if rpes else None,
    }


# --- Rules ---------------------------------------------------------------------------

def propose(metrics: Dict[str, Any], fatigue: str, pain: str, vdot: float, factor: float,
            deload_possible: bool) -> Dict[str, Any]:
    reasons: List[Dict[str, Any]] = []
    compliance = metrics["compliance"]
    low = compliance is not None and compliance < 0.6
    partial = compliance is not None and compliance < 0.8
    if compliance is not None and partial:
        reasons.append({"code": "compliance_low", "pct": round(compliance * 100)})

    # Volume
    deload = False
    if pain == "yes":
        reasons.append({"code": "pain"})
        new_factor = factor * 0.9
        deload = deload_possible
    elif fatigue == "very_tired" or low:
        if fatigue == "very_tired":
            reasons.append({"code": "fatigue_high"})
        new_factor = factor * 0.85
    elif fatigue == "tired" or pain == "mild" or partial:
        if fatigue == "tired":
            reasons.append({"code": "fatigue"})
        if pain == "mild":
            reasons.append({"code": "pain_mild"})
        new_factor = factor * 0.93
    elif factor < 1.0:
        reasons.append({"code": "recovering"})
        new_factor = factor + 0.05
    else:
        new_factor = factor
    # Load: a sharp spike (ACWR > 1.5) cuts volume even if you feel fine
    acwr = metrics.get("acwr")
    spike = acwr is not None and acwr > ACWR_SPIKE
    if spike:
        reasons.append({"code": "load_spike", "ratio": acwr})
        new_factor = min(new_factor, factor * 0.9)
    new_factor = round(min(MAX_FACTOR, max(MIN_FACTOR, new_factor)), 2)

    # VDOT: only with evidence from quality sessions (≥ 2 with data)
    dv = 0.0
    q, rpe = metrics["quality_dev"], metrics["rpe_avg"]
    if q is not None:
        if q >= 0.03 and fatigue == "good" and pain == "no" and not spike and (rpe is None or rpe <= 6):
            dv = 1.0 if q >= 0.05 else 0.5
            reasons.append({"code": "quality_fast", "pct": round(q * 100)})
        elif q <= -0.04 and (fatigue != "good" or (rpe is not None and rpe >= 8)):
            dv = -1.0 if q <= -0.07 else -0.5
            reasons.append({"code": "quality_slow", "pct": round(-q * 100)})

    tips = []
    if acwr is not None and ACWR_HIGH < acwr <= ACWR_SPIKE:
        tips.append({"code": "load_high", "ratio": acwr})
    # Fast easy runs: if they feel hard, slow down; if comfortable and you're fresh, the VDOT fell short,
    # unless quality sessions are slow: then the aerobic base is ahead of speed
    easy = metrics["easy_dev"]
    if easy is not None and easy >= 0.06:
        easy_rpe = metrics.get("easy_rpe")
        comfortable = easy_rpe is not None and easy_rpe <= EASY_COMFORT_RPE and fatigue == "good" and pain == "no"
        quality = metrics.get("quality_mean")
        if not comfortable:
            tips.append({"code": "easy_too_fast", "pct": round(easy * 100)})
        elif quality is not None and quality <= QUALITY_SLOW:
            tips.append({"code": "aerobic_ahead", "pct": round(easy * 100), "q": round(-quality * 100)})
        elif dv == 0:
            tips.append({"code": "easy_comfortable", "pct": round(easy * 100), "rpe": easy_rpe, "vdot": round(vdot, 1)})

    # Fading reps: too fast a start or a target pace still out of reach
    fade = metrics.get("fade")
    if fade is not None and fade >= FADE_TIP:
        tips.append({"code": "fade", "pct": round(fade * 100)})

    # Aerobic efficiency (meters per beat on easy runs) over the plan
    eff = metrics.get("efficiency_change")
    if eff is not None and eff >= EFFICIENCY_TIP:
        tips.append({"code": "efficiency_up", "pct": eff})
    elif eff is not None and eff <= -EFFICIENCY_TIP:
        tips.append({"code": "efficiency_down", "pct": -eff})

    # Estimated form far from the current VDOT: informational only (VDOT changes via the rules above)
    form = metrics.get("form_vdot")
    if form is not None and dv == 0 and abs(form - vdot) >= FORM_GAP_TIP:
        tips.append({"code": "form_above" if form > vdot else "form_below", "form": form, "vdot": round(vdot, 1)})

    changes = dv != 0 or new_factor != factor or deload
    if not changes and not reasons:
        reasons.append({"code": "all_good"})
    return {
        "vdot_from": round(vdot, 1),
        "vdot_to": round(vdot + dv, 1),
        "volume_from": factor,
        "volume_to": new_factor,
        "deload_this_week": deload,
        "changes": changes,
        "reasons": reasons,
        "tips": tips,
    }


# --- Lifecycle ------------------------------------------------------------------------

def create_review(db: Session, plan: TrainingPlan, fatigue: str, pain: str, skip: bool = False) -> Optional[PlanReview]:
    period = due_period(db, plan)
    if not period:
        return None
    week_from, week_to = period
    review = PlanReview(plan_id=plan.id, week_from=week_from, week_to=week_to)
    if skip:
        review.decision = "skipped"
        review.decided_at = datetime.utcnow()
    else:
        metrics = compute_metrics(db, plan, week_from, week_to)
        metrics["acwr"] = plan_service.training_load(db, plan)["ratio"]
        metrics["form_vdot"] = (plan_service.form_view(db, plan)["estimate"] or {}).get("vdot")
        metrics["efficiency_change"] = plan_service.aerobic_view(db, plan)["efficiency"]["change_pct"]
        factor, _ = plan_service.plan_adjustments(plan)
        week_now = plan_service.current_week(plan)
        deload_possible = plan_service.phases_for(plan)[week_now - 1] in ("base", "build", "peak")
        proposal = propose(metrics, fatigue, pain, plan_service.plan_vdot(plan), factor, deload_possible)
        proposal["deload_week"] = week_now if proposal["deload_this_week"] else None
        review.fatigue, review.pain = fatigue, pain
        review.metrics_json = json.dumps(metrics)
        review.proposal_json = json.dumps(proposal)
    db.add(review)
    db.commit()
    return review


def decide(db: Session, plan: TrainingPlan, review: PlanReview, accept: bool) -> bool:
    """Applies (or discards) the proposal. Returns True if the plan changed."""
    review.decision = "accepted" if accept else "declined"
    review.decided_at = datetime.utcnow()
    proposal = json.loads(review.proposal_json or "{}")
    changed = accept and proposal.get("changes")
    if changed:
        factor, deloads = plan_service.plan_adjustments(plan)
        if proposal.get("deload_week"):
            deloads.add(proposal["deload_week"])
        plan.adjust_json = json.dumps({"volume_factor": proposal["volume_to"], "deload_weeks": sorted(deloads)})
        db.commit()
        if proposal["vdot_to"] != proposal["vdot_from"]:
            plan_service.set_plan_vdot(db, plan, proposal["vdot_to"], source="review")
            plan.user.calculated_vdot = proposal["vdot_to"]
        plan_service.regenerate_future(db, plan)
    db.commit()
    return bool(changed)


def review_state(db: Session, plan: TrainingPlan) -> Optional[Dict[str, Any]]:
    """State for the UI: pending proposal, questions or nothing."""
    pending = next((r for r in plan.reviews if r.decision == "pending"), None)
    if pending:
        proposal = json.loads(pending.proposal_json)
        distance, terrain = plan.target_distance, plan.terrain
        proposal["prediction_from"] = predict_race_time_range(proposal["vdot_from"], distance, terrain)["formatted_nominal"]
        proposal["prediction_to"] = predict_race_time_range(proposal["vdot_to"], distance, terrain)["formatted_nominal"]
        return {"stage": "proposal", "id": pending.id, "week_from": pending.week_from, "week_to": pending.week_to,
                "metrics": json.loads(pending.metrics_json), "proposal": proposal}
    period = due_period(db, plan)
    if period:
        return {"stage": "questions", "week_from": period[0], "week_to": period[1],
                "metrics": compute_metrics(db, plan, *period)}
    return None
