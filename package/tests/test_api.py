import json
import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from unittest import mock

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.core.security import COOKIE_NAME, session_token
from app.engine.vdot import get_vdot_from_race
from app.main import app
from app.models.schemas import (
    SCHEMA_VERSION, ActivityLog, GarminDeletion, PlanReview, TrainingPlan, UserProfile, VdotHistory, Workout,
    init_db_migrations,
)
from app.services import plan_service
from app.services.garmin_client import GarminAccount, garmin_accounts


def next_monday() -> date:
    today = date.today()
    return today + timedelta(days=(7 - today.weekday()) % 7 or 7)


class FakeGarmin:
    """Replaces the Garmin network at GarminAccount level (all accounts)."""

    def __init__(self):
        self.uploaded = []
        self.deleted = []
        self.activities = []
        self.delete_fails = False  # simulates Garmin rejecting the deletion (expired session, network...)
        self.upload_fails = False

    def upload_and_schedule(self, acct, payload, day):
        if self.upload_fails:
            raise RuntimeError("API Error 503")
        self.uploaded.append((acct.token_dir.name, payload["workoutName"], day))
        n = len(self.uploaded)
        return f"w{n}", f"s{n}"

    def delete_workout(self, acct, wid, sid):
        if self.delete_fails:
            return False
        self.deleted.append(wid)
        return True

    def reschedule(self, acct, wid, sid, day):
        return f"{sid}-moved"

    def get_running_activities(self, acct, start, end):
        return self.activities


def fake_client(garmin_id, name="Runner"):
    return SimpleNamespace(display_name=garmin_id, full_name=name,
                           client=SimpleNamespace(dump=lambda path: None, load=lambda path: None))


class BaseApiTest(unittest.TestCase):
    def setUp(self):
        with engine.begin() as conn:
            for table in ("plan_races", "garmin_deletions", "vdot_history", "plan_reviews", "activity_logs", "workouts", "training_plans", "user_profiles"):
                conn.execute(text(f"DELETE FROM {table}"))
        self.fake = FakeGarmin()
        plan_service.sync_status = plan_service.SyncStatus()
        f = self.fake
        patches = [
            mock.patch.object(GarminAccount, "is_connected", lambda self: True),
            mock.patch.object(GarminAccount, "upload_and_schedule", lambda self, p, d: f.upload_and_schedule(self, p, d)),
            mock.patch.object(GarminAccount, "delete_workout", lambda self, w, s: f.delete_workout(self, w, s)),
            mock.patch.object(GarminAccount, "reschedule", lambda self, w, s, d: f.reschedule(self, w, s, d)),
            mock.patch.object(GarminAccount, "get_running_activities", lambda self, a, b: f.get_running_activities(self, a, b)),
            mock.patch.object(plan_service.time, "sleep"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.client = TestClient(app)
        self.user_id = self.make_user("garmin-a")
        self.login_as(self.user_id)

    def make_user(self, garmin_id, name="A"):
        db = SessionLocal()
        try:
            u = UserProfile(garmin_user_id=garmin_id, display_name=name, reference_distance="10k",
                            reference_time_sec=3000, calculated_vdot=get_vdot_from_race("10k", 3000))
            db.add(u)
            db.commit()
            return u.id
        finally:
            db.close()

    def login_as(self, user_id):
        self.client.cookies.set(COOKIE_NAME, session_token(user_id))

    def create_plan(self, weeks=8, **extra):
        start = next_monday()
        body = {"target_distance": "10k", "target_date": (start + timedelta(weeks=weeks, days=5)).isoformat(),
                "start_date": start.isoformat(), "weekly_days": [1, 3, 6], "long_run_day": 6,
                "reference_distance": "10k", "reference_time_sec": 3000, **extra}
        res = self.client.post("/api/plans", json=body)
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()["plan_id"]

    def shift_plan(self, plan_id, days):
        """Moves the plan into the past to simulate weeks already run."""
        with engine.begin() as conn:
            conn.execute(text("UPDATE training_plans SET start_date = date(start_date, :d), "
                              "target_date = date(target_date, :d) WHERE id = :p"), {"d": f"-{days} days", "p": plan_id})
            conn.execute(text("UPDATE workouts SET scheduled_date = date(scheduled_date, :d), "
                              "planned_date = date(planned_date, :d) WHERE plan_id = :p"), {"d": f"-{days} days", "p": plan_id})
            conn.execute(text("UPDATE plan_races SET race_date = date(race_date, :d) WHERE plan_id = :p"),
                         {"d": f"-{days} days", "p": plan_id})


class PlanApiTest(BaseApiTest):
    def test_requires_session(self):
        anon = TestClient(app)
        self.assertEqual(anon.get("/api/plans/active").status_code, 401)
        anon.cookies.set(COOKIE_NAME, f"{self.user_id}.forged")
        self.assertEqual(anon.get("/api/me").status_code, 401)

    def test_index_versions_assets_so_updates_are_not_cached(self):
        from app import __version__
        res = TestClient(app).get("/")
        self.assertEqual(res.headers["cache-control"], "no-cache")
        for path in ("/static/css/app.css", "/static/js/help.js", "/static/js/app.js"):
            self.assertIn(f'"{path}?v={__version__}"', res.text)

    def test_progress_is_loaded_apart_and_status_does_not_call_garmin(self):
        self.create_plan()
        active = self.client.get("/api/plans/active").json()
        self.assertFalse({"form", "load", "efficiency", "intensity", "adherence"} & set(active))
        progress = self.client.get("/api/plans/active/progress").json()
        self.assertTrue({"form", "load", "efficiency", "intensity", "adherence", "vo2max"} <= set(progress))
        with mock.patch.object(GarminAccount, "get_personal_records", side_effect=AssertionError("called Garmin")), \
                mock.patch.object(GarminAccount, "get_recent_vo2max", side_effect=AssertionError("called Garmin")):
            self.assertEqual(set(self.client.get("/api/garmin/status").json()), {"connected", "pending_deletions", "name"})
        with mock.patch.object(GarminAccount, "get_personal_records", return_value={"10k": 2900}):
            self.assertEqual(self.client.get("/api/garmin/records").json(), {"pbs": {"10k": 2900}})

    def test_plan_takes_the_event_name_or_a_default(self):
        self.create_plan(name="  Maratón de Santiago  ")
        self.assertEqual(self.client.get("/api/plans/active").json()["plan"]["name"], "Maratón de Santiago")
        self.create_plan(name="   ")
        self.assertTrue(self.client.get("/api/plans/active").json()["plan"]["name"].startswith("10K · "))

    def test_create_plan_syncs_only_the_window(self):
        self.create_plan()
        window_end = date.today() + timedelta(days=plan_service.SYNC_WINDOW_DAYS)
        self.assertTrue(self.fake.uploaded)
        self.assertTrue(all(day <= window_end for _, _, day in self.fake.uploaded))
        data = self.client.get("/api/plans/active").json()
        self.assertEqual(data["sync"]["pending"], 0)
        self.assertEqual(data["weeks"][-1]["phase"], "race")

    def test_cancelled_plan_is_never_synced(self):
        plan_id = self.create_plan()
        on_watch = len(self.fake.uploaded)
        self.assertEqual(self.client.post(f"/api/plans/{plan_id}/cancel").status_code, 200)
        self.assertEqual(len(self.fake.deleted), on_watch)
        self.fake.uploaded.clear()
        plan_service.run_cycle()
        self.assertEqual(self.fake.uploaded, [])
        db = SessionLocal()
        try:
            self.assertEqual({w.status for w in db.query(Workout).filter(Workout.plan_id == plan_id)}, {"missed"})
        finally:
            db.close()

    def test_sync_status_distinguishes_sending_from_failed(self):
        self.create_plan()
        sync = self.client.get("/api/plans/active").json()["sync"]
        self.assertEqual((sync["syncing"], sync["failed"], sync["pending"]), (False, False, 0))
        # While an upload is in progress
        plan_service.sync_status.start(self.user_id)
        self.assertTrue(self.client.get("/api/plans/active").json()["sync"]["syncing"])
        plan_service.sync_status.finish(self.user_id)

    def test_failed_upload_is_reported_until_retry_succeeds(self):
        self.fake.upload_fails = True
        self.create_plan()
        sync = self.client.get("/api/plans/active").json()["sync"]
        self.assertTrue(sync["failed"])
        self.assertFalse(sync["syncing"])
        self.assertGreater(sync["pending"], 0)
        self.fake.upload_fails = False
        res = self.client.post("/api/plans/active/sync").json()
        self.assertGreater(res["synced"], 0)
        sync = self.client.get("/api/plans/active").json()["sync"]
        self.assertEqual((sync["failed"], sync["pending"]), (False, 0))

    def test_new_plan_removes_previous_plan_from_garmin(self):
        self.create_plan()
        old_ids = {f"w{i + 1}" for i in range(len(self.fake.uploaded))}
        self.assertTrue(old_ids)
        self.create_plan(weeks=10)
        self.assertEqual(set(self.fake.deleted), old_ids)
        self.assertEqual(self.client.get("/api/garmin/status").json()["pending_deletions"], 0)

    def test_failed_deletions_are_kept_and_retried(self):
        plan_id = self.create_plan()
        on_watch = len(self.fake.uploaded)
        self.fake.delete_fails = True
        self.client.post(f"/api/plans/{plan_id}/cancel")
        # Garmin failed: the ids are not lost
        self.assertEqual(self.client.get("/api/garmin/status").json()["pending_deletions"], on_watch)
        self.fake.delete_fails = False
        plan_service.run_cycle()  # the hourly cycle retries
        self.assertEqual(len(self.fake.deleted), on_watch)
        self.assertEqual(self.client.get("/api/garmin/status").json()["pending_deletions"], 0)

    def test_retries_stop_after_max_attempts(self):
        plan_id = self.create_plan()
        self.fake.delete_fails = True
        self.client.post(f"/api/plans/{plan_id}/cancel")
        with engine.begin() as conn:
            conn.execute(text("UPDATE garmin_deletions SET attempts = :n"), {"n": plan_service.MAX_DELETE_ATTEMPTS})
        self.fake.delete_fails = False
        plan_service.run_cycle()
        self.assertEqual(self.fake.deleted, [])  # no longer retried automatically; "Clean calendar" re-enables it

    def test_vdot_change_updates_future_paces_and_resyncs(self):
        self.create_plan()
        wid = self.client.get("/api/plans/active").json()["next_workout"]["id"]
        old_steps = self.client.get(f"/api/workouts/{wid}").json()["steps"]
        uploads = len(self.fake.uploaded)
        self.client.put("/api/profile", json={"reference_distance": "10k", "reference_time_sec": 2700})
        self.assertNotEqual(old_steps, self.client.get(f"/api/workouts/{wid}").json()["steps"])
        self.assertGreater(len(self.fake.uploaded), uploads)
        # Only one entry per day, with the latest value and its source
        history = self.client.get("/api/plans/active/progress").json()["form"]["history"]
        self.assertEqual(len(history), 1)
        self.assertEqual((history[0]["source"], history[0]["vdot"]),
                         ("reference", round(get_vdot_from_race("10k", 2700), 1)))

    def test_form_estimate_and_predictions(self):
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 35)
        db = SessionLocal()
        try:
            from app.engine.workouts import expected_pace
            done = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.scheduled_date < date.today(),
                                            Workout.session_type.in_(["tempo", "intervals"])).all()
            for w in done:
                w.status = "completed"
                pace = int(expected_pace(json.loads(w.spec_json), w.vdot + 2))  # performs like VDOT +2
                db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id=f"f{w.id}",
                                   start_time=w.scheduled_date, actual_distance_km=w.target_distance_km,
                                   actual_duration_sec=int(pace * w.target_distance_km), avg_pace_sec_km=pace))
            db.commit()
        finally:
            db.close()
        form = self.client.get("/api/plans/active/progress").json()["form"]
        self.assertGreaterEqual(len(form["sessions"]), 3)
        self.assertAlmostEqual(form["estimate"]["vdot"], form["vdot"] + 2, delta=0.3)
        self.assertEqual([p["distance"] for p in form["predictions"]], ["5k", "10k", "21k", "42k"])
        target = next(p for p in form["predictions"] if p["is_target"])
        self.assertEqual(target["distance"], "10k")
        self.assertLess(target["form"], target["plan"])  # faster (same h:mm:ss / mm:ss format)

    def test_language_switch(self):
        self.create_plan()
        self.client.put("/api/profile", json={"language": "en"})
        titles = [w["title"] for wk in self.client.get("/api/plans/active").json()["weeks"] for w in wk["workouts"]]
        self.assertTrue(any(t.startswith(("Easy run", "Long run")) for t in titles))

    def test_move_status_and_rpe(self):
        self.create_plan()
        target = self.client.get("/api/plans/active").json()["weeks"][2]["workouts"][0]
        new_date = (date.fromisoformat(target["date"]) + timedelta(days=1)).isoformat()
        self.assertEqual(self.client.post(f"/api/workouts/{target['id']}/move", json={"new_date": new_date}).json()["date"], new_date)
        self.assertEqual(self.client.post(f"/api/workouts/{target['id']}/status", json={"status": "completed"}).json()["status"], "completed")
        self.assertEqual(self.client.post(f"/api/workouts/{target['id']}/status", json={"status": "bogus"}).status_code, 400)
        self.assertEqual(self.client.post(f"/api/workouts/{target['id']}/rpe", json={"rpe": 7}).json()["rpe"], 7)
        self.assertEqual(self.client.post(f"/api/workouts/{target['id']}/rpe", json={"rpe": 11}).status_code, 400)

    def test_move_only_between_today_and_race(self):
        self.create_plan()
        data = self.client.get("/api/plans/active").json()
        wid = data["weeks"][2]["workouts"][0]["id"]
        race = date.fromisoformat(data["plan"]["target_date"])
        for bad in (date.today() - timedelta(days=1), race + timedelta(days=1)):
            res = self.client.post(f"/api/workouts/{wid}/move", json={"new_date": bad.isoformat()})
            self.assertEqual(res.json()["detail"], "invalid_date")
        self.assertEqual(self.client.post(f"/api/workouts/{wid}/move", json={"new_date": race.isoformat()}).status_code, 200)

    def test_short_run_does_not_complete_a_session(self):
        plan_id = self.create_plan()
        self.shift_plan(plan_id, 7)
        db = SessionLocal()
        try:
            w = db.query(Workout).filter(Workout.plan_id == plan_id).order_by(Workout.scheduled_date).first()
            day, wid, km = w.scheduled_date, w.id, w.target_distance_km
        finally:
            db.close()
        self.fake.activities = [{"activityId": 77, "startTimeLocal": f"{day} 07:00:00", "distance": km * 1000 * 0.3,
                                 "duration": 900.0, "activityType": {"typeKey": "running"}}]
        plan_service.run_cycle()
        db = SessionLocal()
        try:
            self.assertNotEqual(db.get(Workout, wid).status, "completed")
            self.assertIsNone(db.query(ActivityLog).filter(ActivityLog.garmin_activity_id == "77").one().workout_id)
        finally:
            db.close()

    def test_validation(self):
        start = next_monday()
        base = {"target_distance": "10k", "start_date": start.isoformat(), "weekly_days": [1, 3, 6], "long_run_day": 6}
        short = self.client.post("/api/plans", json={**base, "target_date": (start + timedelta(days=10)).isoformat()})
        self.assertEqual(short.json()["detail"], "plan_too_short")
        bad_time = self.client.post("/api/plans", json={**base, "target_date": (start + timedelta(weeks=8)).isoformat(),
                                                        "reference_distance": "5k", "reference_time_sec": 6150})
        self.assertEqual(bad_time.json()["detail"], "invalid_time")

    def test_reconcile_matches_activity_and_owner(self):
        plan_id = self.create_plan()
        self.shift_plan(plan_id, 7)
        db = SessionLocal()
        try:
            w = db.query(Workout).filter(Workout.plan_id == plan_id).order_by(Workout.scheduled_date).first()
            day = w.scheduled_date
        finally:
            db.close()
        self.fake.activities = [{"activityId": 99, "startTimeLocal": f"{day} 07:00:00", "distance": 6000.0,
                                 "duration": 1900.0, "activityType": {"typeKey": "running"}}]
        plan_service.run_cycle()
        db = SessionLocal()
        try:
            log = db.query(ActivityLog).filter(ActivityLog.garmin_activity_id == "99").one()
            self.assertEqual(log.user_id, self.user_id)
            self.assertEqual(log.workout.status, "completed")
            self.assertEqual(log.avg_pace_sec_km, 317)
        finally:
            db.close()

    def test_unplanned_runs_count_as_extra_weekly_volume(self):
        plan_id = self.create_plan()
        self.shift_plan(plan_id, 7)
        db = SessionLocal()
        try:
            start = db.get(TrainingPlan, plan_id).start_date
        finally:
            db.close()
        tue = start + timedelta(days=1)
        # Tuesday's first run is the session; the second is extra; the one before the plan doesn't count
        self.fake.activities = [
            {"activityId": 500, "startTimeLocal": f"{tue} 07:00:00", "distance": 7000.0, "duration": 2400.0},
            {"activityId": 501, "startTimeLocal": f"{tue} 19:00:00", "distance": 5200.0, "duration": 1800.0},
            {"activityId": 502, "startTimeLocal": f"{start - timedelta(days=3)} 07:00:00", "distance": 8000.0, "duration": 2800.0},
        ]
        plan_service.run_cycle()
        weeks = self.client.get("/api/plans/active").json()["weeks"]
        self.assertEqual(weeks[0]["extra_km"], 5.2)
        self.assertEqual(sum(w["extra_km"] for w in weeks), 5.2)

    def test_migrations_drop_legacy_columns_and_keep_data(self):
        self.create_plan()
        sessions = len(self.fake.uploaded)
        with engine.begin() as conn:  # pre-migration database, like the one on the NAS
            for table, col in (("user_profiles", "pace_easy_min_sec INTEGER NOT NULL DEFAULT 0"),
                               ("training_plans", "gender VARCHAR"),
                               ("training_plans", "review_every_weeks INTEGER DEFAULT 2"),
                               ("workouts", "session_title VARCHAR NOT NULL DEFAULT ''")):
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col}")
            conn.exec_driver_sql("PRAGMA user_version = 0")
        init_db_migrations(engine)
        init_db_migrations(engine)  # idempotent
        with engine.connect() as conn:
            self.assertEqual(conn.exec_driver_sql("PRAGMA user_version").scalar(), SCHEMA_VERSION)
            cols = {r[1] for t in ("user_profiles", "training_plans", "workouts")
                    for r in conn.exec_driver_sql(f"PRAGMA table_info({t})")}
        self.assertFalse(cols & {"pace_easy_min_sec", "gender", "session_title", "review_every_weeks"})
        data = self.client.get("/api/plans/active").json()
        self.assertTrue(data["active"])
        self.assertTrue(any(w["workouts"] for w in data["weeks"]))
        self.assertEqual(len(self.fake.uploaded), sessions)
        self.make_user("garmin-after-migration")  # without the legacy NOT NULL columns profiles can still be created


class WorkLapsApiTest(BaseApiTest):
    def test_quality_session_is_judged_by_its_work_blocks(self):
        from tests.test_engine import structured_laps
        from app.engine.workouts import expected_work_pace
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 35)
        db = SessionLocal()
        try:
            w = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.session_type == "intervals",
                                         Workout.scheduled_date < date.today()).first()
            spec = json.loads(w.spec_json)
            rep = expected_work_pace(spec, w.vdot) * spec["dist_m"] / 1000
            laps = structured_laps([rep] * spec["reps"], rep_m=spec["dist_m"])
            w.status = "completed"
            # Very slow average pace (standing rests): without laps it would look like a bad session
            db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id="laps1",
                               start_time=w.scheduled_date, actual_distance_km=8, actual_duration_sec=8 * 420,
                               avg_pace_sec_km=420))
            db.commit()
            wid = w.id
        finally:
            db.close()

        before = self.client.get(f"/api/workouts/{wid}").json()["actual"]
        self.assertEqual(before["pace_check"]["basis"], "avg")
        self.assertIsNone(before["work"])

        calls = []
        with mock.patch.object(GarminAccount, "get_laps", lambda acct, aid: calls.append(aid) or laps):
            db = SessionLocal()
            try:
                self.assertEqual(plan_service.fetch_missing_laps(db, db.get(TrainingPlan, plan_id)), 1)
                self.assertEqual(plan_service.fetch_missing_laps(db, db.get(TrainingPlan, plan_id)), 0)  # already read
            finally:
                db.close()
        self.assertEqual(calls, ["laps1"])
        after = self.client.get(f"/api/workouts/{wid}").json()["actual"]
        self.assertEqual((after["pace_check"]["basis"], after["pace_check"]["level"]), ("work", "ok"))
        self.assertEqual(len(after["work"]["blocks"]), spec["reps"])

    def test_deleted_activity_is_not_fetched_again(self):
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 35)
        db = SessionLocal()
        try:
            w = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.session_type == "tempo",
                                         Workout.scheduled_date < date.today()).first()
            w.status = "completed"
            db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id="gone",
                               start_time=w.scheduled_date, actual_distance_km=8, actual_duration_sec=2400,
                               avg_pace_sec_km=300))
            db.commit()
            with mock.patch.object(GarminAccount, "get_laps", lambda acct, aid: None):
                self.assertEqual(plan_service.fetch_missing_laps(db, db.get(TrainingPlan, plan_id)), 1)
            self.assertEqual(db.query(ActivityLog).filter_by(garmin_activity_id="gone").one().laps_json, "[]")
        finally:
            db.close()


class BRaceApiTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.plan_id = self.create_plan(weeks=8)  # 9 weeks: 8 is taper, 9 is the race
        self.b_date = next_monday() + timedelta(weeks=3, days=6)  # Sunday of week 4

    def sessions(self):
        db = SessionLocal()
        try:
            return {w.scheduled_date: (w.session_type, json.loads(w.spec_json))
                    for w in db.query(Workout).filter(Workout.plan_id == self.plan_id)}
        finally:
            db.close()

    def add(self, day=None, distance="10k", name="10k del barrio"):
        return self.client.post("/api/plans/active/races", json={
            "race_date": (day or self.b_date).isoformat(), "distance": distance, "name": name})

    def test_add_b_race_reshapes_the_plan(self):
        before = self.sessions()
        res = self.add()
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual([(r["date"], r["distance"], r["name"]) for r in res.json()["races"]],
                         [(self.b_date.isoformat(), "10k", "10k del barrio")])
        after = self.sessions()
        self.assertEqual(after[self.b_date], ("race", {"kind": "race", "distance": "10k", "terrain": "flat",
                                                        "priority": "b"}))
        self.assertEqual(before[self.b_date][0], "long_run")
        active = self.client.get("/api/plans/active").json()
        self.assertEqual(active["weeks"][3]["phase"], "tuneup")
        self.assertEqual(len(active["races"]), 1)
        self.assertIsNone(active["race_proposal"])
        # The taper replaces the previous Thursday's tempo with an easy run
        thursday = self.b_date - timedelta(days=3)
        self.assertNotEqual(before[thursday][0], "easy")
        self.assertEqual(after[thursday][0], "easy")

    def test_b_race_validation(self):
        self.assertEqual(self.add(date.today()).json()["detail"], "b_race_in_past")
        self.assertEqual(self.add(next_monday() + timedelta(weeks=7, days=2)).json()["detail"], "b_race_too_late")
        self.assertEqual(self.add(distance="42k").json()["detail"], "invalid_params")
        self.assertEqual(self.add().status_code, 200)
        self.assertEqual(self.add(self.b_date + timedelta(days=7)).json()["detail"], "b_race_too_close")

    def test_delete_b_race_restores_the_plan(self):
        before = self.sessions()
        race_id = self.add().json()["races"][0]["id"]
        self.assertEqual(self.client.delete(f"/api/plans/active/races/{race_id}").json(), {"races": []})
        self.assertEqual(self.sessions(), before)
        self.assertEqual(self.client.delete(f"/api/plans/active/races/{race_id}").status_code, 404)

    def test_b_race_result_proposes_and_applies_vdot(self):
        race_id = self.add().json()["races"][0]["id"]
        self.shift_plan(self.plan_id, (self.b_date - date.today()).days + 2)  # the race was two days ago
        b_date = date.today() - timedelta(days=2)
        db = SessionLocal()
        try:
            w = db.query(Workout).filter(Workout.plan_id == self.plan_id, Workout.scheduled_date == b_date).one()
            self.assertEqual(w.session_type, "race")
            w.status = "completed"
            db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id="b1",
                               start_time=b_date, actual_distance_km=10.02, actual_duration_sec=2820,
                               avg_pace_sec_km=281))
            db.commit()
        finally:
            db.close()
        active = self.client.get("/api/plans/active").json()
        proposal = active["race_proposal"]
        self.assertEqual(proposal["id"], race_id)
        self.assertEqual(proposal["result"]["time_sec"], 2820)
        self.assertEqual(proposal["vdot_to"], round(get_vdot_from_race("10k", 2820), 1))
        self.assertGreater(proposal["vdot_to"], proposal["vdot_from"])
        self.assertEqual(self.client.delete(f"/api/plans/active/races/{race_id}").status_code, 409)  # already past

        res = self.client.post(f"/api/plans/active/races/{race_id}/vdot", json={"accept": True}).json()
        self.assertEqual(res, {"decision": "applied", "vdot": proposal["vdot_to"]})
        active = self.client.get("/api/plans/active").json()
        self.assertIsNone(active["race_proposal"])
        self.assertEqual(active["plan"]["vdot"], proposal["vdot_to"])
        self.assertEqual(self.client.get("/api/profile").json()["reference_time_sec"], 2820)
        self.assertEqual(self.client.post(f"/api/plans/active/races/{race_id}/vdot",
                                          json={"accept": False}).status_code, 404)
        # History takes the goal race as the result, not the B race
        db = SessionLocal()
        try:
            self.assertIsNone(plan_service.plan_summary(db, db.get(TrainingPlan, self.plan_id))["race"])
        finally:
            db.close()


class HistoryTest(BaseApiTest):
    def move_race_to(self, plan_id, day):
        db = SessionLocal()
        try:
            target = db.get(TrainingPlan, plan_id).target_date
        finally:
            db.close()
        self.shift_plan(plan_id, (target - day).days)

    def test_plan_finishes_after_race_and_goes_to_history(self):
        plan_id = self.create_plan(weeks=8)
        self.move_race_to(plan_id, date.today() - timedelta(days=1))
        self.assertTrue(self.client.get("/api/plans/active").json()["active"])  # grace period to log the race
        self.assertEqual(self.client.get("/api/plans/history").json()["plans"], [])

        self.move_race_to(plan_id, date.today() - timedelta(days=plan_service.FINISH_AFTER_DAYS))
        db = SessionLocal()
        try:
            race = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.session_type == "race").one()
            race.status = "completed"
            db.add(ActivityLog(user_id=self.user_id, workout_id=race.id, garmin_activity_id="race1",
                               start_time=race.scheduled_date, actual_distance_km=10.05, actual_duration_sec=2950,
                               avg_pace_sec_km=294))
            db.commit()
        finally:
            db.close()
        self.assertFalse(self.client.get("/api/plans/active").json()["active"])
        plans = self.client.get("/api/plans/history").json()["plans"]
        self.assertEqual(len(plans), 1)
        p = plans[0]
        self.assertEqual((p["id"], p["status"]), (plan_id, "completed"))
        self.assertEqual(p["race"]["time_sec"], 2950)
        self.assertEqual(p["adherence"]["sessions"]["done"], 1)
        self.assertGreater(p["adherence"]["sessions"]["total"], 1)  # the rest, not done
        self.assertEqual(p["vdot_start"], p["vdot_end"])

    def test_closing_on_race_day_completes_and_before_cancels(self):
        plan_id = self.create_plan(weeks=8)
        self.move_race_to(plan_id, date.today())
        self.assertEqual(self.client.post(f"/api/plans/{plan_id}/cancel").json()["status"], "completed")
        other = self.create_plan(weeks=8)
        self.assertEqual(self.client.post(f"/api/plans/{other}/cancel").json()["status"], "cancelled")
        # A cancelled plan with no sessions done is not shown in history
        self.assertEqual([p["id"] for p in self.client.get("/api/plans/history").json()["plans"]], [plan_id])

    def test_sync_imports_race_and_plan_can_be_finished(self):
        # The race is run a day early: the sync button imports it
        # and the plan can then be finished (completed, not cancelled)
        plan_id = self.create_plan(weeks=8)
        self.move_race_to(plan_id, date.today() + timedelta(days=1))
        with engine.begin() as conn:  # everything before already done: the activity can only be the race
            conn.execute(text("UPDATE workouts SET status = 'completed' WHERE plan_id = :p AND session_type != 'race'"),
                         {"p": plan_id})
        self.assertFalse(self.client.get("/api/plans/active").json()["plan"]["finished"])
        self.fake.activities = [{"activityId": 99, "startTimeLocal": f"{date.today().isoformat()}T09:00:00",
                                 "distance": 10050, "duration": 2950}]
        res = self.client.post("/api/plans/active/sync").json()
        self.assertEqual(res["imported"], 1)
        self.assertTrue(self.client.get("/api/plans/active").json()["plan"]["finished"])
        self.assertEqual(self.client.post(f"/api/plans/{plan_id}/cancel").json()["status"], "completed")
        self.assertEqual([p["id"] for p in self.client.get("/api/plans/history").json()["plans"]], [plan_id])

    def test_history_is_per_user(self):
        plan_id = self.create_plan(weeks=8)
        self.move_race_to(plan_id, date.today())
        self.client.post(f"/api/plans/{plan_id}/cancel")
        self.login_as(self.make_user("garmin-b", "B"))
        self.assertEqual(self.client.get("/api/plans/history").json()["plans"], [])


class MultiUserTest(BaseApiTest):
    def test_users_are_isolated(self):
        self.create_plan()
        wid_a = self.client.get("/api/plans/active").json()["next_workout"]["id"]
        plan_a = self.client.get("/api/plans/active").json()["plan"]["id"]

        user_b = self.make_user("garmin-b", "B")
        self.login_as(user_b)
        self.assertFalse(self.client.get("/api/plans/active").json()["active"])
        self.assertEqual(self.client.get(f"/api/workouts/{wid_a}").status_code, 404)
        self.assertEqual(self.client.post(f"/api/plans/{plan_a}/cancel").status_code, 404)

        self.create_plan(weeks=10)
        self.login_as(self.user_id)
        self.assertEqual(self.client.get("/api/plans/active").json()["plan"]["id"], plan_a)
        uploaders = {u for u, _, _ in self.fake.uploaded}
        self.assertEqual(uploaders, {str(self.user_id), str(user_b)})  # per-user tokens

    def test_login_finds_or_creates_profile(self):
        anon = TestClient(app)
        with mock.patch.object(garmin_accounts, "login", return_value={"client": fake_client("garmin-a", "Rodrigo")}):
            res = anon.post("/api/auth/login", json={"email": "a@b.c", "password": "x"})
        self.assertEqual(res.status_code, 200, res.text)
        me = anon.get("/api/me").json()
        self.assertEqual((me["id"], me["name"]), (self.user_id, "Rodrigo"))  # same Garmin account, same profile

        other = TestClient(app)
        with mock.patch.object(garmin_accounts, "login", return_value={"client": fake_client("garmin-other")}):
            other.post("/api/auth/login", json={"email": "c@d.e", "password": "x"})
        self.assertNotEqual(other.get("/api/me").json()["id"], self.user_id)

    def test_mfa_flow_and_logout(self):
        anon = TestClient(app)
        with mock.patch.object(garmin_accounts, "login", return_value={"mfa_session": "s1"}):
            self.assertEqual(anon.post("/api/auth/login", json={"email": "a", "password": "b"}).json()["status"], "mfa_required")
        with mock.patch.object(garmin_accounts, "complete_mfa", return_value=fake_client("garmin-a")):
            anon.post("/api/auth/mfa", json={"session_id": "s1", "mfa_code": "123456"})
        self.assertEqual(anon.get("/api/me").json()["id"], self.user_id)
        anon.post("/api/auth/logout")
        self.assertEqual(anon.get("/api/me").status_code, 401)

    def test_delete_account(self):
        self.create_plan()
        self.assertEqual(self.client.delete("/api/me").status_code, 200)
        db = SessionLocal()
        try:
            self.assertIsNone(db.get(UserProfile, self.user_id))
            self.assertEqual(db.query(TrainingPlan).filter(TrainingPlan.user_id == self.user_id).count(), 0)
            self.assertEqual(db.query(VdotHistory).filter(VdotHistory.user_id == self.user_id).count(), 0)
        finally:
            db.close()


class ReviewTest(BaseApiTest):
    def _plan_in_week_3(self, done_fraction=1.0, rpe=5, faster=0.0):
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 21)  # today falls in week 3
        db = SessionLocal()
        try:
            rows = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.week_number <= 2) \
                .order_by(Workout.scheduled_date).all()
            for i, w in enumerate(rows):
                if i < round(len(rows) * done_fraction):
                    w.status, w.rpe = "completed", rpe
                    spec = json.loads(w.spec_json)
                    from app.engine.workouts import expected_pace
                    pace = int(expected_pace(spec, w.vdot) * (1 - faster))
                    db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id=f"a{w.id}",
                                       start_time=date.today(), actual_distance_km=w.target_distance_km,
                                       actual_duration_sec=int(pace * w.target_distance_km), avg_pace_sec_km=pace))
                else:
                    w.status = "missed"
            db.commit()
        finally:
            db.close()
        return plan_id

    def test_review_due_and_all_good(self):
        self._plan_in_week_3()
        review = self.client.get("/api/plans/active").json()["review"]
        self.assertEqual(review["stage"], "questions")
        self.assertEqual((review["week_from"], review["week_to"]), (1, 2))
        self.assertEqual(review["metrics"]["compliance"], 1.0)
        prop = self.client.post("/api/plans/active/review", json={"fatigue": "good", "pain": "no"}).json()
        self.assertEqual(prop["stage"], "proposal")
        self.assertFalse(prop["proposal"]["changes"])
        self.client.post(f"/api/plans/active/review/{prop['id']}", json={"accept": True})
        self.assertIsNone(self.client.get("/api/plans/active").json()["review"])

    def test_active_plan_reports_adherence_and_pace(self):
        self._plan_in_week_3(done_fraction=0.5)
        data = self.client.get("/api/plans/active").json()
        a = self.client.get("/api/plans/active/progress").json()["adherence"]
        views = [w for wk in data["weeks"] for w in wk["workouts"]]
        done = [w for w in views if w["status"] == "completed"]
        missed = [w for w in views if w["status"] == "missed"]
        self.assertEqual(a["sessions"]["done"], len(done))
        self.assertEqual(a["sessions"]["total"], len(done) + len(missed))
        self.assertEqual(a["sessions"]["pct"], data["stats"]["compliance"])
        self.assertEqual(a["pace"]["ok"], a["pace"]["checked"])
        self.assertGreater(a["pace"]["checked"], 0)
        self.assertTrue(all(w["pace"] in ("ok", None) for w in done))
        detail = self.client.get(f"/api/workouts/{done[0]['id']}").json()
        self.assertEqual(detail["actual"]["pace_check"]["level"], "ok")

    def test_active_plan_reports_training_load(self):
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 35)  # today falls in week 5-6: more than 4 weeks of history
        db = SessionLocal()
        try:
            for w in db.query(Workout).filter(Workout.plan_id == plan_id, Workout.scheduled_date < date.today()):
                w.status = "completed"
                db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id=f"a{w.id}",
                                   start_time=w.scheduled_date, actual_distance_km=w.target_distance_km,
                                   actual_duration_sec=w.estimated_duration_min * 60, avg_pace_sec_km=330))
            db.commit()
        finally:
            db.close()
        load = self.client.get("/api/plans/active/progress").json()["load"]
        self.assertIsNotNone(load["ratio"])
        self.assertIn(load["zone"], ("low", "optimal", "caution", "high"))
        self.assertEqual(load["available_in_days"], 0)
        self.assertLess(load["ratio"], 1.5)  # following the plan does not trigger the alert
        prop = self.client.post("/api/plans/active/review", json={"fatigue": "good", "pain": "no"}).json()
        self.assertEqual(prop["metrics"]["acwr"], load["ratio"])

    def test_efficiency_and_intensity(self):
        plan_id = self.create_plan(weeks=10)
        self.shift_plan(plan_id, 35)
        db = SessionLocal()
        try:
            rows = db.query(Workout).filter(Workout.plan_id == plan_id, Workout.scheduled_date < date.today()) \
                .order_by(Workout.scheduled_date).all()
            for i, w in enumerate(rows):
                w.status = "completed"
                db.add(ActivityLog(user_id=self.user_id, workout_id=w.id, garmin_activity_id=f"e{w.id}",
                                   start_time=w.scheduled_date, actual_distance_km=w.target_distance_km,
                                   actual_duration_sec=w.estimated_duration_min * 60, avg_pace_sec_km=330,
                                   avg_hr=150 - i))  # heart rate drops: efficiency improves
            db.commit()
        finally:
            db.close()
        data = self.client.get("/api/plans/active/progress").json()
        eff = data["efficiency"]
        self.assertGreaterEqual(len(eff["series"]), 4)
        self.assertGreater(eff["change_pct"], 0)
        mix = data["intensity"]
        self.assertEqual(mix["easy_pct"] + mix["moderate_pct"] + mix["hard_pct"], 100)
        self.assertGreater(mix["hard_pct"], 0)

    def test_new_plan_load_is_still_building(self):
        self.create_plan()
        load = self.client.get("/api/plans/active/progress").json()["load"]
        self.assertIsNone(load["ratio"])
        self.assertGreater(load["available_in_days"], 0)

    def test_fast_quality_raises_vdot(self):
        self._plan_in_week_3(faster=0.06, rpe=5)
        prop = self.client.post("/api/plans/active/review", json={"fatigue": "good", "pain": "no"}).json()["proposal"]
        self.assertEqual(prop["vdot_to"] - prop["vdot_from"], 1.0)
        self.assertNotEqual(prop["prediction_from"], prop["prediction_to"])
        review = self.client.get("/api/plans/active").json()["review"]
        self.client.post(f"/api/plans/active/review/{review['id']}", json={"accept": True})
        history = self.client.get("/api/plans/active/progress").json()["form"]["history"]
        self.assertEqual(history[-1]["source"], "review")
        self.assertEqual(history[-1]["vdot"], prop["vdot_to"])

    def test_fatigue_reduces_future_volume_when_accepted(self):
        self._plan_in_week_3(done_fraction=0.5)
        before = self.client.get("/api/plans/active").json()
        future_km = sum(w["planned_km"] for w in before["weeks"][3:-2])
        state = self.client.post("/api/plans/active/review", json={"fatigue": "very_tired", "pain": "no"}).json()
        self.assertEqual(state["proposal"]["volume_to"], 0.85)
        self.client.post(f"/api/plans/active/review/{state['id']}", json={"accept": True})
        after = self.client.get("/api/plans/active").json()
        self.assertEqual(after["plan"]["volume_factor"], 0.85)
        self.assertLess(sum(w["planned_km"] for w in after["weeks"][3:-2]), future_km)

    def test_pain_inserts_deload_this_week(self):
        self._plan_in_week_3()
        state = self.client.post("/api/plans/active/review", json={"fatigue": "good", "pain": "yes"}).json()
        self.assertEqual(state["proposal"]["deload_week"], 3)
        self.client.post(f"/api/plans/active/review/{state['id']}", json={"accept": True})
        self.assertEqual(self.client.get("/api/plans/active").json()["weeks"][2]["phase"], "deload")

    def test_decline_and_skip(self):
        self._plan_in_week_3()
        state = self.client.post("/api/plans/active/review", json={"fatigue": "very_tired", "pain": "no"}).json()
        self.client.post(f"/api/plans/active/review/{state['id']}", json={"accept": False})
        self.assertEqual(self.client.get("/api/plans/active").json()["plan"]["volume_factor"], 1.0)
        db = SessionLocal()
        try:
            self.assertEqual(db.query(PlanReview).one().decision, "declined")
        finally:
            db.close()

    def test_skipped_review_waits_for_next_period(self):
        self._plan_in_week_3()
        self.client.post("/api/plans/active/review", json={"skip": True})
        self.assertIsNone(self.client.get("/api/plans/active").json()["review"])


if __name__ == "__main__":
    unittest.main()


class BackupApiTest(BaseApiTest):
    def test_download_is_a_consistent_sqlite_copy(self):
        self.create_plan()
        res = self.client.get("/api/backup/download")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.content.startswith(b"SQLite format 3\x00"))
        self.assertIn("garmin-companion-", res.headers["content-disposition"])

    def test_restore_replaces_data_and_keeps_safety_copy(self):
        self.create_plan()
        snapshot = self.client.get("/api/backup/download").content
        other = self.make_user("garmin-b", "B")

        res = self.client.post("/api/backup/restore", content=snapshot,
                               headers={"Content-Type": "application/octet-stream"})
        self.assertEqual(res.status_code, 200, res.text)
        db = SessionLocal()
        try:
            self.assertIsNone(db.get(UserProfile, other))
            self.assertEqual(db.query(TrainingPlan).count(), 1)
        finally:
            db.close()
        from app.api.backup import DATA_DIR
        self.assertTrue((DATA_DIR / res.json()["safety_copy"]).exists())
        self.assertEqual(self.client.get("/api/me").status_code, 200)

    def test_restore_rejects_invalid_files(self):
        for payload in (b"not a database", b"SQLite format 3\x00" + b"\x00" * 100):
            res = self.client.post("/api/backup/restore", content=payload)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()["detail"], "invalid_backup")
        self.assertIsNotNone(self.client.get("/api/me").json()["id"])

    def test_backup_requires_session(self):
        anon = TestClient(app)
        self.assertEqual(anon.get("/api/backup/download").status_code, 401)
        self.assertEqual(anon.post("/api/backup/restore", content=b"x").status_code, 401)

    def test_backup_is_admin_only(self):
        self.assertTrue(self.client.get("/api/me").json()["admin"])  # the server's first profile
        self.login_as(self.make_user("garmin-b", "B"))
        self.assertFalse(self.client.get("/api/me").json()["admin"])
        self.assertEqual(self.client.get("/api/backup/download").json()["detail"], "admin_only")
        self.assertEqual(self.client.post("/api/backup/restore", content=b"x").status_code, 403)


class DetectLanguageTest(unittest.TestCase):
    def test_explicit_then_header_then_default(self):
        from app.api.auth import detect_language
        self.assertEqual(detect_language("es", "en-US,en;q=0.9"), "es")
        self.assertEqual(detect_language("xx", "es-CL,es;q=0.9"), "es")
        self.assertEqual(detect_language(None, "fr-FR,de"), "en")
        self.assertEqual(detect_language(None, None), "en")
        self.assertEqual(detect_language("EN-us", None), "en")
