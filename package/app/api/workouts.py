from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import current_user
from app.models.schemas import TrainingPlan, UserProfile, Workout
from app.services import plan_service

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


class MoveRequest(BaseModel):
    new_date: date


class StatusRequest(BaseModel):
    status: str  # completed | scheduled


class RpeRequest(BaseModel):
    rpe: int  # 1-10


def _get(db: Session, user: UserProfile, workout_id: int) -> Workout:
    w = db.query(Workout).join(TrainingPlan).filter(Workout.id == workout_id, TrainingPlan.user_id == user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="workout_not_found")
    return w


@router.get("/{workout_id}")
def get_workout(workout_id: int, user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    w = _get(db, user, workout_id)
    return plan_service.workout_view(w, plan_service.language(w.plan), plan_service.plan_vdot(w.plan), detail=True)


@router.post("/{workout_id}/move")
def move(workout_id: int, req: MoveRequest, user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    w = _get(db, user, workout_id)
    if w.status == "completed":
        raise HTTPException(status_code=400, detail="workout_completed")
    if not date.today() <= req.new_date <= w.plan.target_date:
        raise HTTPException(status_code=400, detail="invalid_date")
    plan_service.move_workout(db, w, req.new_date)
    if w.plan.status == "active":
        plan_service.sync_window(db, w.plan)
    return {"status": "moved", "date": w.scheduled_date.isoformat()}


@router.post("/{workout_id}/status")
def set_status(workout_id: int, req: StatusRequest, user: UserProfile = Depends(current_user),
               db: Session = Depends(get_db)):
    if req.status not in ("completed", "scheduled"):
        raise HTTPException(status_code=400, detail="invalid_status")
    w = _get(db, user, workout_id)
    w.status = req.status
    db.commit()
    plan_service.mark_missed(db, w.plan)
    return {"status": w.status}


@router.post("/{workout_id}/rpe")
def set_rpe(workout_id: int, req: RpeRequest, user: UserProfile = Depends(current_user),
            db: Session = Depends(get_db)):
    if not 1 <= req.rpe <= 10:
        raise HTTPException(status_code=400, detail="invalid_params")
    w = _get(db, user, workout_id)
    w.rpe = req.rpe
    db.commit()
    return {"rpe": w.rpe}
