from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.auth import LANGUAGES
from app.core.database import get_db
from app.core.security import current_user
from app.engine.vdot import calculate_training_paces, get_vdot_from_race, seconds_to_time
from app.models.schemas import UserProfile
from app.services import plan_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    reference_distance: Optional[str] = None
    reference_time_sec: Optional[int] = None
    language: Optional[str] = None


def set_reference(db: Session, user: UserProfile, distance: str, time_sec: int) -> bool:
    """Updates the reference time. Returns True if the VDOT changed."""
    try:
        vdot = get_vdot_from_race(distance, time_sec)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_time")
    changed = abs(vdot - (user.calculated_vdot or 0)) > 0.01
    user.reference_distance = distance.lower()
    user.reference_time_sec = time_sec
    user.calculated_vdot = vdot
    db.commit()
    return changed


def profile_view(user: UserProfile) -> dict:
    p = calculate_training_paces(user.calculated_vdot)
    fmt = seconds_to_time
    return {
        "reference_distance": user.reference_distance,
        "reference_time_sec": user.reference_time_sec,
        "reference_time": seconds_to_time(user.reference_time_sec),
        "vdot": round(user.calculated_vdot, 1),
        "language": user.preferred_language or "es",
        "paces": {
            "easy": f"{fmt(p['easy_min_sec'])}–{fmt(p['easy_max_sec'])}",
            "marathon": fmt(p["marathon_sec"]),
            "threshold": fmt(p["threshold_sec"]),
            "interval": fmt(p["interval_sec"]),
            "repetition": fmt(p["repetition_sec"]),
        },
    }


@router.get("")
def get_profile(user: UserProfile = Depends(current_user)):
    return profile_view(user)


@router.put("")
def update_profile(req: ProfileUpdate, background: BackgroundTasks,
                   user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    resync = False

    if req.reference_distance and req.reference_time_sec:
        if set_reference(db, user, req.reference_distance, req.reference_time_sec):
            plan = plan_service.get_active_plan(db, user.id)
            if plan:
                plan_service.set_plan_vdot(db, plan, user.calculated_vdot)
                resync = True
            else:
                plan_service.record_vdot(db, user.id, user.calculated_vdot, "reference")

    if req.language:
        lang = req.language.lower()
        if lang not in LANGUAGES:
            raise HTTPException(status_code=400, detail="unsupported_language")
        if lang != user.preferred_language:
            user.preferred_language = lang
            db.commit()
            resync = True

    if resync:
        plan_service.sync_status.start(user.id)
        background.add_task(plan_service.resync_user, user.id)
    return profile_view(user)
