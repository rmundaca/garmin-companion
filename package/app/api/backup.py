"""
Download and restore of the full database (all profiles) from Settings.
The SQLite backup API is used both ways: a consistent copy even with data in the WAL,
without closing or replacing the file the engine has open.
"""
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.config import DATA_DIR
from app.core.database import Base, engine
from app.core.security import admin_user
from app.models.schemas import UserProfile, init_db_migrations

logger = logging.getLogger("api_backup")
router = APIRouter(prefix="/api/backup", tags=["backup"])

MAX_UPLOAD = 100 * 1024 * 1024
SQLITE_MAGIC = b"SQLite format 3\x00"
KEEP_SAFETY_COPIES = 3


def _sqlite(raw) -> sqlite3.Connection:
    # driver_connection since SQLAlchemy 1.4.24; before that, .connection
    return getattr(raw, "driver_connection", None) or raw.connection


def _copy_live_db_to(dest: Path):
    raw = engine.raw_connection()
    try:
        out = sqlite3.connect(dest)
        try:
            _sqlite(raw).backup(out)
        finally:
            out.close()
    finally:
        raw.close()


def _validate(path: Path):
    with open(path, "rb") as f:
        if f.read(16) != SQLITE_MAGIC:
            raise HTTPException(status_code=400, detail="invalid_backup")
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            ok = conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            conn.close()
    except sqlite3.DatabaseError:
        raise HTTPException(status_code=400, detail="invalid_backup")
    if not ok or UserProfile.__tablename__ not in tables:
        raise HTTPException(status_code=400, detail="invalid_backup")


def _prune_safety_copies():
    copies = sorted(DATA_DIR.glob("app-before-restore-*.db"))
    for old in copies[:-KEEP_SAFETY_COPIES]:
        old.unlink(missing_ok=True)


@router.get("/download")
def download(user: UserProfile = Depends(admin_user)):
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    tmp = DATA_DIR / f"download-{stamp}.tmp"
    _copy_live_db_to(tmp)
    return FileResponse(tmp, media_type="application/x-sqlite3",
                        filename=f"garmin-companion-{stamp}.db",
                        background=BackgroundTask(tmp.unlink, missing_ok=True))


@router.post("/restore")
async def restore(request: Request, user: UserProfile = Depends(admin_user)):
    # Raw body (the file as is): no multipart, with a size cap
    body = bytearray()
    async for chunk in request.stream():
        body += chunk
        if len(body) > MAX_UPLOAD:
            raise HTTPException(status_code=413, detail="backup_too_large")

    upload = DATA_DIR / "restore-upload.tmp"
    upload.write_bytes(body)
    try:
        _validate(upload)

        # Safety copy of the current DB in case the restore was not the intended one
        safety = DATA_DIR / f"app-before-restore-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
        _copy_live_db_to(safety)
        _prune_safety_copies()

        src = sqlite3.connect(upload)
        raw = engine.raw_connection()
        try:
            src.backup(_sqlite(raw))
        finally:
            raw.close()
            src.close()
    finally:
        upload.unlink(missing_ok=True)

    # Pooled connections cache the previous schema; an older copy may need migrations
    engine.dispose()
    Base.metadata.create_all(bind=engine)
    init_db_migrations(engine)
    logger.info(f"Database restored by user {user.id}; previous copy in {safety.name}")
    return {"status": "restored", "safety_copy": safety.name}
