"""User session: HMAC-signed cookie (no external dependencies)."""
import hashlib
import hmac
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import DATA_DIR
from app.core.database import get_db
from app.models.schemas import UserProfile

COOKIE_NAME = "gc_session"
COOKIE_MAX_AGE = 365 * 24 * 3600


def _load_secret() -> bytes:
    path = DATA_DIR / "secret.key"
    if not path.exists():
        path.write_text(secrets.token_hex(32), encoding="utf-8")
    return path.read_text(encoding="utf-8").strip().encode()


SECRET = _load_secret()


def _sign(value: str) -> str:
    return hmac.new(SECRET, value.encode(), hashlib.sha256).hexdigest()


def session_token(user_id: int) -> str:
    return f"{user_id}.{_sign(str(user_id))}"


def read_session(token: Optional[str]) -> Optional[int]:
    if not token or "." not in token:
        return None
    uid, sig = token.split(".", 1)
    if not uid.isdigit() or not hmac.compare_digest(sig, _sign(uid)):
        return None
    return int(uid)


def set_session(response: Response, user_id: int):
    response.set_cookie(COOKIE_NAME, session_token(user_id), max_age=COOKIE_MAX_AGE,
                        httponly=True, samesite="lax")


def clear_session(response: Response):
    response.delete_cookie(COOKIE_NAME)


def current_user(request: Request, db: Session = Depends(get_db)) -> UserProfile:
    uid = read_session(request.cookies.get(COOKIE_NAME))
    user = db.get(UserProfile, uid) if uid else None
    if not user:
        raise HTTPException(status_code=401, detail="not_authenticated")
    return user


def is_admin(db: Session, user: UserProfile) -> bool:
    """The server's oldest profile (whoever installed it) administers everyone's data."""
    return user.id == db.query(func.min(UserProfile.id)).scalar()


def admin_user(user: UserProfile = Depends(current_user), db: Session = Depends(get_db)) -> UserProfile:
    if not is_admin(db, user):
        raise HTTPException(status_code=403, detail="admin_only")
    return user
