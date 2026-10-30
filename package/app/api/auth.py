"""
Identity = Garmin account. Signing in with Garmin (credentials or token) finds or creates the
profile linked to that account and sets a signed session cookie in the browser.
"""
import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import clear_session, current_user, is_admin, set_session
from app.engine.vdot import get_vdot_from_race
from app.models.schemas import ActivityLog, UserProfile
from app.services import plan_service
from app.services.garmin_client import garmin_accounts, identity

logger = logging.getLogger("api_auth")
router = APIRouter(tags=["auth"])


LANGUAGES = ("es", "en")
DEFAULT_LANGUAGE = "en"


class LoginRequest(BaseModel):
    email: str
    password: str
    language: Optional[str] = None


class MfaRequest(BaseModel):
    session_id: str
    mfa_code: str
    language: Optional[str] = None


class TokenLogin(BaseModel):
    token_json: str
    language: Optional[str] = None


def detect_language(requested: Optional[str], accept_language: Optional[str]) -> str:
    """Language for a new profile: the one sent by the browser, else the Accept-Language header."""
    candidates = [requested or ""]
    for part in (accept_language or "").split(","):
        candidates.append(part.split(";")[0])
    for value in candidates:
        code = value.strip()[:2].lower()
        if code in LANGUAGES:
            return code
    return DEFAULT_LANGUAGE


def _sign_in(client, db: Session, response: Response, background: BackgroundTasks, language: str) -> dict:
    try:
        garmin_id, name = identity(client)
    except Exception as e:
        logger.error(f"Could not read Garmin identity: {e}")
        raise HTTPException(status_code=400, detail="login_failed")

    user = db.query(UserProfile).filter(UserProfile.garmin_user_id == garmin_id).first()
    if not user:
        user = UserProfile(garmin_user_id=garmin_id, reference_distance="10k", reference_time_sec=3000,
                           calculated_vdot=get_vdot_from_race("10k", 3000), preferred_language=language)
        db.add(user)
    user.display_name = name
    db.commit()

    garmin_accounts.get(user.id).attach(client)
    set_session(response, user.id)
    background.add_task(plan_service.run_cycle, user.id)
    return {"status": "success"}


@router.get("/api/me")
def me(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    return {
        "id": user.id,
        "name": user.display_name,
        "language": user.preferred_language or "es",
        "garmin_connected": garmin_accounts.get(user.id).is_connected(),
        "admin": is_admin(db, user),
    }


@router.post("/api/auth/login")
def login(req: LoginRequest, request: Request, response: Response, background: BackgroundTasks,
          db: Session = Depends(get_db)):
    try:
        res = garmin_accounts.login(req.email, req.password)
    except Exception as e:
        logger.error(f"Garmin login failed: {e}")
        raise HTTPException(status_code=400, detail="login_failed")
    if "mfa_session" in res:
        return {"status": "mfa_required", "session_id": res["mfa_session"]}
    language = detect_language(req.language, request.headers.get("accept-language"))
    return _sign_in(res["client"], db, response, background, language)


@router.post("/api/auth/mfa")
def mfa(req: MfaRequest, request: Request, response: Response, background: BackgroundTasks,
        db: Session = Depends(get_db)):
    try:
        client = garmin_accounts.complete_mfa(req.session_id, req.mfa_code)
    except KeyError:
        raise HTTPException(status_code=400, detail="mfa_expired")
    except Exception as e:
        logger.error(f"Garmin MFA failed: {e}")
        raise HTTPException(status_code=400, detail="mfa_failed")
    language = detect_language(req.language, request.headers.get("accept-language"))
    return _sign_in(client, db, response, background, language)


@router.post("/api/auth/token")
def token_login(req: TokenLogin, request: Request, response: Response, background: BackgroundTasks,
                db: Session = Depends(get_db)):
    try:
        client = garmin_accounts.login_with_token(req.token_json.strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_token_json")
    except Exception as e:
        logger.error(f"Garmin token rejected: {e}")
        raise HTTPException(status_code=400, detail="invalid_token")
    language = detect_language(req.language, request.headers.get("accept-language"))
    return _sign_in(client, db, response, background, language)


@router.post("/api/auth/logout")
def logout(response: Response):
    clear_session(response)
    return {"status": "signed_out"}


@router.delete("/api/me")
def delete_account(response: Response, background: BackgroundTasks,
                   user: UserProfile = Depends(current_user), db: Session = Depends(get_db)):
    """Deletes the user, their plans, activities and tokens. Removes pending sessions from Garmin."""
    plan = plan_service.get_active_plan(db, user.id)
    if plan:
        plan_service.close_plan(db, plan)
    plan_service.delete_pending(db, user.id)
    db.query(ActivityLog).filter(ActivityLog.user_id == user.id).delete(synchronize_session=False)
    garmin_accounts.forget(user.id)
    db.delete(user)
    db.commit()
    clear_session(response)
    return {"status": "deleted"}
