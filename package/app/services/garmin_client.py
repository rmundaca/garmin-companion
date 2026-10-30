"""
Garmin Connect integration.

Each user has their own GarminAccount (client, tokens in data/tokens/<user_id>/ and
caches). Login does not know the user yet: it returns an authenticated client and the Garmin
identity (displayName), which the API uses to find or create the profile.
"""
import json
import logging
import shutil
import threading
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import garminconnect

from app.core.config import TOKEN_DIR
from app.engine.workouts import is_app_title

logger = logging.getLogger("garmin_client")

CACHE_TTL_SEC = 900
MFA_TTL_SEC = 600
RESTORE_RETRY_SEC = 900  # wait between attempts to restore the saved session if Garmin did not respond
PB_TYPES = {3: "5k", 4: "10k", 5: "21k", 7: "42k"}
PB_KEYS = {"running5k": "5k", "running10k": "10k", "runningHalfMarathon": "21k", "runningMarathon": "42k"}


def identity(client: garminconnect.Garmin) -> Tuple[str, str]:
    """(stable Garmin account id, display name)."""
    if not getattr(client, "display_name", None):
        client._load_profile_and_settings()
    garmin_id = str(client.display_name or "")
    if not garmin_id:
        raise RuntimeError("identity_unavailable")
    return garmin_id, (getattr(client, "full_name", None) or "Garmin")


def _is_not_found(e: Exception) -> bool:
    return "404" in str(e) or getattr(getattr(e, "response", None), "status_code", None) == 404


class GarminAccount:
    def __init__(self, token_dir: Path):
        self.token_dir = token_dir
        self.client: Optional[garminconnect.Garmin] = None
        self._next_restore = 0.0
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    # --- Session ---------------------------------------------------------

    def is_connected(self) -> bool:
        """Cheap: loads the tokens from disk once. If Garmin does not respond (e.g. the NAS booted
        before the network) it retries every RESTORE_RETRY_SEC instead of giving up as disconnected."""
        if self.client is not None:
            return True
        with self._lock:
            if self.client is None and time.time() >= self._next_restore and any(self.token_dir.glob("*.json")):
                self._next_restore = time.time() + RESTORE_RETRY_SEC
                try:
                    client = garminconnect.Garmin()
                    client.login(tokenstore=str(self.token_dir))
                    self.client = client
                except Exception as e:
                    logger.warning(f"Could not restore Garmin session ({self.token_dir.name}): {e}")
        return self.client is not None

    def attach(self, client: garminconnect.Garmin):
        self.token_dir.mkdir(parents=True, exist_ok=True)
        path = str(self.token_dir)
        client.client.dump(path)
        # Loading from the folder makes garminconnect save every refreshed token there. Otherwise
        # the (single-use) refresh token stays only in memory and a spent one is loaded on restart.
        client.client.load(path)
        self.client = client
        self._cache.clear()

    def forget(self):
        self.client = None
        self._cache.clear()
        shutil.rmtree(self.token_dir, ignore_errors=True)

    # --- Metrics (cached) ------------------------------------------------

    def _cached(self, key: str, fn):
        hit = self._cache.get(key)
        if hit and time.time() - hit[0] < CACHE_TTL_SEC:
            return hit[1]
        try:
            value = fn()
        except Exception as e:
            logger.warning(f"Could not get {key} from Garmin: {e}")
            return hit[1] if hit else None
        self._cache[key] = (time.time(), value)
        return value

    def get_personal_records(self) -> Dict[str, int]:
        if not self.is_connected():
            return {}

        def fetch():
            pbs = {}
            for rec in self.client.get_personal_record() or []:
                key = PB_TYPES.get(rec.get("typeId")) or PB_KEYS.get(rec.get("typeKey"))
                if key and rec.get("value"):
                    pbs[key] = int(rec["value"])
            return pbs

        return self._cached("pbs", fetch) or {}

    def get_recent_vo2max(self) -> Optional[float]:
        if not self.is_connected():
            return None

        def fetch():
            generic = (self.client.get_stats_and_body(date.today().isoformat()) or {}).get("generic", {}) or {}
            vo2 = generic.get("vo2MaxPreciseValue") or generic.get("vo2MaxValue")
            return float(vo2) if vo2 else None

        return self._cached("vo2max", fetch)

    def get_running_activities(self, start: date, end: date) -> List[Dict[str, Any]]:
        """Running activities (includes trail, treadmill and track)."""
        acts = self.client.get_activities_by_date(start.isoformat(), end.isoformat()) or []
        return [a for a in acts if "running" in ((a.get("activityType") or {}).get("typeKey") or "")]

    def get_laps(self, activity_id: str) -> Optional[List[Dict[str, Any]]]:
        """Activity laps in compact form. With a structured watch workout
        each step generates its laps, with their type (WARMUP, ACTIVE, RECOVERY, COOLDOWN...) and their
        step index. None if the activity no longer exists in Garmin."""
        try:
            laps = (self.client.get_activity_splits(activity_id) or {}).get("lapDTOs") or []
        except Exception as e:
            if _is_not_found(e):
                return None
            raise
        return [{
            "type": lap.get("intensityType"),
            "m": round(lap.get("distance") or 0, 1),
            "s": round(lap.get("duration") or 0, 1),
            "hr": int(lap["averageHR"]) if lap.get("averageHR") else None,
            "step": lap.get("wktStepIndex"),
            # Grade-adjusted pace (sec/km): the flat-ground equivalent
            "gs": round(1000 / lap["avgGradeAdjustedSpeed"]) if lap.get("avgGradeAdjustedSpeed") else None,
        } for lap in laps]

    # --- Workouts ---------------------------------------------------------

    def upload_and_schedule(self, payload: Dict[str, Any], day: date) -> Tuple[str, Optional[str]]:
        res = self.client.upload_workout(payload)
        workout_id = str(res.get("workoutId") or "")
        if not workout_id:
            raise RuntimeError(f"Unexpected response when uploading workout: {res}")
        try:
            sched = self.client.schedule_workout(workout_id, day.isoformat())
        except Exception:
            # Don't leave orphaned workouts in the Garmin library
            self.delete_workout(workout_id, None)
            raise
        sid = sched.get("workoutScheduleId") or sched.get("scheduleId")
        return workout_id, (str(sid) if sid else None)

    def reschedule(self, workout_id: str, schedule_id: Optional[str], day: date) -> Optional[str]:
        if schedule_id:
            try:
                self.client.unschedule_workout(schedule_id)
            except Exception as e:
                logger.warning(f"Could not unschedule {schedule_id}: {e}")
        sched = self.client.schedule_workout(workout_id, day.isoformat())
        sid = sched.get("workoutScheduleId") or sched.get("scheduleId")
        return str(sid) if sid else None

    def delete_workout(self, workout_id: Optional[str], schedule_id: Optional[str]) -> bool:
        """Removes the session from the calendar and deletes the workout from the Garmin library.
        Returns True if it no longer exists in Garmin (deleted now or earlier)."""
        for method in ("unschedule_workout", "delete_workout"):
            if not hasattr(self.client, method):
                logger.error(f"The installed garminconnect version lacks {method}(): "
                             "workouts cannot be deleted from Garmin. Update the package.")
                return False
        if schedule_id:
            try:
                self.client.unschedule_workout(schedule_id)
            except Exception as e:
                if not _is_not_found(e):
                    logger.warning(f"Could not unschedule {schedule_id}: {e}")
        if not workout_id:
            return True
        try:
            self.client.delete_workout(workout_id)
            return True
        except Exception as e:
            if _is_not_found(e):
                return True
            logger.error(f"Could not delete workout {workout_id} from Garmin: {e}")
            return False

    def clean_app_workouts(self, from_date: date, known_ids: Set[str], months_ahead: int = 12) -> int:
        """Deletes future workouts created by this app from the Garmin calendar
        (by known id or title pattern). Does not touch other workouts."""
        removed = 0
        start = from_date.isoformat()
        for offset in range(months_ahead):
            month_index = from_date.month - 1 + offset
            year, month = from_date.year + month_index // 12, month_index % 12 + 1
            try:
                items = (self.client.get_scheduled_workouts(year, month) or {}).get("calendarItems", [])
            except Exception as e:
                logger.warning(f"Could not read calendar {year}-{month}: {e}")
                continue
            for item in items:
                if item.get("itemType") != "workout" or (item.get("date") or "") < start:
                    continue
                wid = str(item.get("workoutId") or "")
                if wid not in known_ids and not is_app_title(item.get("title")):
                    continue
                if self.delete_workout(wid or None, str(item["id"]) if item.get("id") else None):
                    removed += 1
                time.sleep(0.2)
        logger.info(f"Calendar cleanup: {removed} workouts removed since {start}")
        return removed


class GarminAccounts:
    """Per-user account registry and login flow (before the user is known)."""

    def __init__(self, root: Path):
        self.root = root
        self._accounts: Dict[int, GarminAccount] = {}
        self._pending_mfa: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, user_id: int) -> GarminAccount:
        with self._lock:
            if user_id not in self._accounts:
                self._accounts[user_id] = GarminAccount(self.root / str(user_id))
            return self._accounts[user_id]

    def forget(self, user_id: int):
        self.get(user_id).forget()
        with self._lock:
            self._accounts.pop(user_id, None)

    def login(self, email: str, password: str) -> Dict[str, Any]:
        self._purge_mfa()
        client = garminconnect.Garmin(email=email, password=password, return_on_mfa=True)
        mfa_status, _ = client.login()
        if mfa_status == "needs_mfa":
            session_id = str(uuid.uuid4())
            self._pending_mfa[session_id] = {"client": client, "created": time.time()}
            return {"mfa_session": session_id}
        return {"client": client}

    def complete_mfa(self, session_id: str, code: str) -> garminconnect.Garmin:
        self._purge_mfa()
        pending = self._pending_mfa.pop(session_id, None)
        if not pending:
            raise KeyError("mfa_expired")
        client = pending["client"]
        client.resume_login(None, code.strip())
        return client

    def login_with_token(self, token_json: str) -> garminconnect.Garmin:
        parsed = json.loads(token_json)
        if not isinstance(parsed, dict):
            raise ValueError("invalid_token_json")
        client = garminconnect.Garmin()
        client.login(tokenstore=json.dumps(parsed))
        return client

    def _purge_mfa(self):
        now = time.time()
        for sid in [s for s, p in self._pending_mfa.items() if now - p["created"] > MFA_TTL_SEC]:
            self._pending_mfa.pop(sid, None)


garmin_accounts = GarminAccounts(TOKEN_DIR)

# garminconnect calendar functions depend on its version (delete/unschedule
# arrived in 0.3.0): log it at startup.
REQUIRED_METHODS = ("upload_workout", "schedule_workout", "unschedule_workout", "delete_workout",
                    "get_scheduled_workouts")


def log_library_support():
    try:
        from importlib.metadata import version
        installed = version("garminconnect")
    except Exception:
        installed = "unknown"
    missing = [m for m in REQUIRED_METHODS if not hasattr(garminconnect.Garmin, m)]
    if missing:
        logger.error(f"garminconnect {installed}: missing {', '.join(missing)}. "
                     "Workouts cannot be removed from Garmin; garminconnect >= 0.3 is required.")
    else:
        logger.info(f"garminconnect {installed}: calendar functions available")
