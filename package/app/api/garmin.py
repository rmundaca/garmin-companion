import logging
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import current_user
from app.models.schemas import GarminDeletion, TrainingPlan, UserProfile, Workout
from app.services import plan_service
from app.services.garmin_client import garmin_accounts

logger = logging.getLogger("api_garmin")
router = APIRouter(prefix="/api/garmin", tags=["garmin"])


@router.get("/status")
def status(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """No Garmin calls: requested when the app opens and must not wait on the network."""
    return {
        "connected": garmin_accounts.get(user.id).is_connected(),
        "pending_deletions": plan_service.pending_deletions(db, user.id),
        "name": user.display_name,
    }


@router.get("/records")
def records(user: UserProfile = Depends(current_user)):
    """Garmin personal records, to suggest the reference time in the new-plan wizard."""
    acct = garmin_accounts.get(user.id)
    return {"pbs": acct.get_personal_records() if acct.is_connected() else {}}


@router.post("/clean-calendar")
def clean_calendar(background: BackgroundTasks, user: UserProfile = Depends(current_user),
                   db: Session = Depends(get_db)):
    """Deletes future app-created workouts from Garmin and re-uploads the current window."""
    acct = garmin_accounts.get(user.id)
    if not acct.is_connected():
        raise HTTPException(status_code=400, detail="garmin_not_connected")
    today = date.today()
    future = db.query(Workout).join(TrainingPlan).filter(
        TrainingPlan.user_id == user.id,
        Workout.scheduled_date >= today,
        Workout.status != "completed",
    ).all()
    queued = db.query(GarminDeletion).filter(GarminDeletion.user_id == user.id).all()
    known = {w.garmin_workout_id for w in future if w.garmin_workout_id}
    known |= {q.garmin_workout_id for q in queued if q.garmin_workout_id}
    try:
        removed = acct.clean_app_workouts(today, known)
    except Exception as e:
        logger.error(f"Error cleaning calendar: {e}")
        raise HTTPException(status_code=500, detail="clean_failed")
    for w in future:
        w.garmin_workout_id = None
        w.garmin_schedule_id = None
    for q in queued:  # another full round of retries (already deleted ones return 404 and leave the queue)
        q.attempts = 0
    db.commit()
    plan_service.sync_status.start(user.id)
    background.add_task(plan_service.delete_from_garmin, user.id)
    background.add_task(plan_service.sync_user, user.id)
    return {"removed": removed}
