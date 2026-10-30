import unittest
from datetime import date, datetime, timedelta

from app.engine.periodization import assign_days, b_race_error, count_weeks, generate_plan, week_phases, LONG_RUN
from app.engine.stats import (
    adherence, efficiency_trend, form_estimate, hard_fraction, intensity_distribution, load_status,
    meters_per_beat, pace_check, session_load, session_vdot, work_pace, work_summary,
)
from app.engine.vdot import calculate_training_paces, get_vdot_from_race, predict_race_time_range
from app.engine.workouts import expected_work_pace, garmin_payload, is_app_title, render
from app.services.plan_service import match_workout, parse_activity
from app.services.review_service import propose


class PlanCalendarTest(unittest.TestCase):
    def test_workouts_stay_between_start_and_race(self):
        start, race = date(2026, 9, 30), date(2026, 12, 5)  # Wednesday → Saturday
        sessions = generate_plan("10k", start, race, [1, 3, 6], 6)
        dates = [s["scheduled_date"] for s in sessions]
        self.assertGreaterEqual(min(dates), start)
        self.assertEqual(max(dates), race)
        self.assertEqual(sessions[-1]["session_type"], "race")
        self.assertEqual(sessions[-1]["week_number"], count_weeks(start, race))

    def test_rest_on_race_eve(self):
        race = date(2026, 12, 6)  # Sunday
        sessions = generate_plan("21k", date(2026, 9, 28), race, [0, 2, 5, 6], 6)
        self.assertNotIn(race - timedelta(days=1), [s["scheduled_date"] for s in sessions])

    def test_one_session_per_day(self):
        sessions = generate_plan("42k", date(2026, 9, 28), date(2027, 2, 21), [1, 2, 4, 5, 6], 6)
        dates = [s["scheduled_date"] for s in sessions]
        self.assertEqual(len(dates), len(set(dates)))

    def test_phases(self):
        phases = week_phases(12, "21k")
        self.assertEqual(phases[-1], "race")
        self.assertEqual(phases[-3:-1], ["taper", "taper"])
        self.assertIn("deload", phases)
        self.assertEqual(phases[0], "base")
        self.assertEqual(week_phases(12, "21k", "frequent_recent").count("deload"), 2)

    def test_long_run_progression_is_gradual(self):
        sessions = generate_plan("21k", date(2026, 9, 28), date(2027, 1, 17), [1, 3, 6], 6)
        phases = week_phases(count_weeks(date(2026, 9, 28), date(2027, 1, 17)), "21k")
        longs = {s["week_number"]: s["spec"]["km"] for s in sessions if s["session_type"] == "long_run"}
        max_step = LONG_RUN["21k"][2]
        for w in range(2, len(phases)):
            if phases[w - 1] in ("base", "build", "peak") and phases[w - 2] in ("base", "build", "peak"):
                self.assertLessEqual(longs[w] - longs[w - 1], max_step + 0.05)

    def test_quality_days_away_from_long_run(self):
        roles = assign_days([2, 4, 5], 6)  # Wed, Fri, Sat + Sunday long run
        self.assertEqual(roles[2], "q1")
        self.assertEqual(roles[5], "easy")


class BRaceTest(unittest.TestCase):
    START, RACE = date(2026, 9, 28), date(2027, 1, 17)  # Monday → Sunday, 16-week half marathon
    DAYS = [1, 3, 4, 6]

    def plan(self, b_races=(), **kw):
        return generate_plan("21k", self.START, self.RACE, self.DAYS, 6, b_races=b_races, **kw)

    def by_date(self, sessions):
        return {s["scheduled_date"]: s for s in sessions}

    def test_b_race_is_scheduled_with_sharpening_and_recovery(self):
        b = date(2026, 11, 22)  # Sunday of week 8: replaces the long run
        sessions = self.by_date(self.plan([(b, "10k")]))
        race = sessions[b]
        self.assertEqual(race["session_type"], "race")
        self.assertEqual(race["spec"], {"kind": "race", "distance": "10k", "terrain": "flat", "priority": "b"})
        self.assertEqual(race["week_number"], 8)
        self.assertNotIn(b - timedelta(days=1), sessions)  # rest the day before
        for d, s in sessions.items():
            if -3 <= (d - b).days <= 3 and d != b:
                self.assertEqual(s["session_type"], "easy", d)
        # Outside the window, quality sessions match the plan without a B race
        plain = self.by_date(self.plan())
        thursday_after = b + timedelta(days=4)
        self.assertEqual(sessions[thursday_after], plain[thursday_after])
        self.assertEqual(sum(1 for s in sessions.values() if s["session_type"] == "race"), 2)

    def test_half_marathon_b_race_rests_the_next_day(self):
        b = date(2026, 11, 12)  # Thursday
        sessions = self.by_date(self.plan([(b, "21k")]))
        self.assertNotIn(b + timedelta(days=1), sessions)
        self.assertTrue(all(s["session_type"] == "easy" for d, s in sessions.items() if 1 < (d - b).days <= 6))

    def test_b_race_week_replaces_long_run_and_neighbouring_deload(self):
        b = date(2026, 11, 12)  # Thursday of week 7: the cycle's deload (week 8) is skipped
        phases = week_phases(16, "21k", tuneup_weeks=[7])
        self.assertEqual(phases[6], "tuneup")
        self.assertNotEqual(phases[7], "deload")
        self.assertEqual(phases[3], "deload")
        sessions = self.plan([(b, "10k")])
        week7 = [s for s in sessions if s["week_number"] == 7]
        self.assertFalse(any(s["session_type"] == "long_run" for s in week7))
        # With a 5k the long run stays, shortened as in a deload
        sessions5 = self.plan([(b, "5k")])
        plain = self.by_date(self.plan())
        long5 = [s for s in sessions5 if s["week_number"] == 7 and s["session_type"] == "long_run"]
        self.assertEqual(len(long5), 1)
        self.assertLess(long5[0]["spec"]["km"], plain[long5[0]["scheduled_date"]]["spec"]["km"])

    def test_one_session_per_day_with_b_races(self):
        sessions = self.plan([(date(2026, 10, 25), "5k"), (date(2026, 11, 22), "10k")])
        dates = [s["scheduled_date"] for s in sessions]
        self.assertEqual(len(dates), len(set(dates)))

    def test_b_race_validation(self):
        err = lambda d, dist="10k", others=(): b_race_error(self.START, self.RACE, "21k", d, dist, others)
        self.assertIsNone(err(date(2026, 11, 15)))
        self.assertEqual(err(date(2026, 11, 15), "42k"), "invalid_params")
        self.assertEqual(err(date(2026, 10, 1)), "b_race_too_early")  # week 1
        self.assertIsNone(err(date(2026, 12, 27)))  # week 13: last training week
        self.assertEqual(err(date(2026, 12, 29)), "b_race_too_late")  # week 14: taper
        self.assertEqual(err(date(2026, 11, 15), others=[date(2026, 11, 8)]), "b_race_too_close")
        self.assertIsNone(err(date(2026, 11, 22), others=[date(2026, 11, 8)]))

    def test_b_race_text(self):
        r = render({"kind": "race", "distance": "10k", "terrain": "flat", "priority": "b"}, 45, "es")
        self.assertEqual(r["title"], "Carrera 10K")
        self.assertTrue(is_app_title(r["title"]))
        self.assertIn("preparación", r["description"])


class RenderTest(unittest.TestCase):
    spec = {"kind": "intervals", "reps": 5, "dist_m": 800, "rest_sec": 90}

    def test_garmin_payload_uses_pace_zone(self):
        payload = garmin_payload(self.spec, 45, "es")
        steps = payload["workoutSegments"][0]["workoutSteps"]
        work = [s for s in steps if s["stepType"]["stepTypeKey"] == "interval"]
        self.assertEqual(len(work), 5)
        for s in work:
            self.assertEqual(s["targetType"], {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"})
            self.assertLess(s["targetValueOne"], s["targetValueTwo"])  # slow < fast (m/s)
        rec = [s for s in steps if s["stepType"]["stepTypeKey"] == "recovery"]
        self.assertEqual(len(rec), 4)
        self.assertTrue(all(s["targetType"]["workoutTargetTypeKey"] == "no.target" for s in rec))

    def test_easy_runs_have_no_watch_target_but_show_reference(self):
        for kind in ("easy", "long_run"):
            spec = {"kind": kind, "km": 8}
            step = garmin_payload(spec, 45, "es")["workoutSegments"][0]["workoutSteps"][0]
            self.assertEqual(step["targetType"]["workoutTargetTypeKey"], "no.target")
            self.assertTrue(render(spec, 45, "es")["steps"][0]["pace"].startswith("~"))
        self.assertFalse(render(self.spec, 45, "es")["steps"][1]["pace"].startswith("~"))

    def test_languages_and_vdot_change_render(self):
        es, en = render(self.spec, 45, "es"), render(self.spec, 45, "en")
        self.assertEqual(es["title"], "Series 5x800m")
        self.assertEqual(en["title"], "Intervals 5x800m")
        faster = render(self.spec, 50, "es")
        self.assertNotEqual(es["steps"][1]["pace"], faster["steps"][1]["pace"])
        self.assertLess(faster["duration_min"], es["duration_min"])

    def test_every_generated_title_is_recognized_as_app_workout(self):
        for lang in ("es", "en"):
            for s in generate_plan("21k", date(2026, 9, 28), date(2027, 1, 17), [1, 3, 5, 6], 6, "hilly"):
                self.assertTrue(is_app_title(render(s["spec"], 45, lang)["title"]), s["spec"])

    def test_app_title_patterns(self):
        for legacy in ("Series 6x800m - VO2max", "Tempo Run 5.0 km - Umbral", "Cuestas 6x60s - Fuerza & Potencia",
                       "Rodaje Suave 6.0 km", "Long Run 14.0 km"):
            self.assertTrue(is_app_title(legacy), legacy)
        for foreign in ("Carrera del domingo", "Tempo con amigos", "Series en pista", "Race"):
            self.assertFalse(is_app_title(foreign), foreign)


class VdotTest(unittest.TestCase):
    def test_rejects_implausible_results(self):
        with self.assertRaises(ValueError):
            get_vdot_from_race("5k", 6150)
        with self.assertRaises(ValueError):
            get_vdot_from_race("42k", 3600)
        self.assertAlmostEqual(get_vdot_from_race("10k", 3000), 39.9, delta=0.2)

    def test_prediction_roundtrip(self):
        pred = predict_race_time_range(get_vdot_from_race("10k", 3000), "10k")
        self.assertAlmostEqual(pred["nominal_sec"], 3000, delta=5)


class GarminDeleteTest(unittest.TestCase):
    def account(self, client):
        from pathlib import Path
        from app.services.garmin_client import GarminAccount
        acct = GarminAccount(Path("unused"))
        acct.client = client
        return acct

    def test_not_found_counts_as_deleted(self):
        class Client:
            def unschedule_workout(self, sid): raise RuntimeError("API Error 404")
            def delete_workout(self, wid): raise RuntimeError("API Error 404")
        self.assertTrue(self.account(Client()).delete_workout("1", "2"))

    def test_errors_and_old_library_report_failure(self):
        class Failing:
            def unschedule_workout(self, sid): return {}
            def delete_workout(self, wid): raise RuntimeError("API Error 500")

        class OldLibrary:  # garminconnect < 0.3: no delete methods
            def upload_workout(self, payload): return {}
        with self.assertLogs("garmin_client", level="ERROR"):
            self.assertFalse(self.account(Failing()).delete_workout("1", "2"))
        with self.assertLogs("garmin_client", level="ERROR"):
            self.assertFalse(self.account(OldLibrary()).delete_workout("1", "2"))


class GarminSessionTest(unittest.TestCase):
    def test_attach_makes_the_library_persist_refreshed_tokens(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace
        from app.services.garmin_client import GarminAccount
        calls = []
        lib = SimpleNamespace(dump=lambda p: calls.append(("dump", p)), load=lambda p: calls.append(("load", p)))
        with tempfile.TemporaryDirectory() as tmp:
            acct = GarminAccount(Path(tmp) / "1")
            acct.attach(SimpleNamespace(client=lib))
            # load() from the folder is what makes garminconnect save every refresh there
            self.assertEqual(calls, [("dump", str(acct.token_dir)), ("load", str(acct.token_dir))])
            self.assertTrue(acct.is_connected())

    def test_restore_is_retried_after_a_failure(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from app.services import garmin_client
        attempts = []

        class Garmin:
            def login(self, tokenstore):
                attempts.append(tokenstore)
                if len(attempts) == 1:
                    raise ConnectionError("network down at startup")

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(garmin_client.garminconnect, "Garmin", Garmin), \
                mock.patch.object(garmin_client.time, "time") as now:
            acct = garmin_client.GarminAccount(Path(tmp))
            (acct.token_dir / "garmin_tokens.json").write_text("{}")
            now.return_value = 1000.0
            with self.assertLogs("garmin_client", level="WARNING"):
                self.assertFalse(acct.is_connected())
            self.assertFalse(acct.is_connected())  # Garmin is not called again within the wait
            self.assertEqual(len(attempts), 1)
            now.return_value = 1000.0 + garmin_client.RESTORE_RETRY_SEC
            self.assertTrue(acct.is_connected())
            self.assertEqual(len(attempts), 2)


class ActivityTest(unittest.TestCase):
    def test_pace_uses_duration_and_distance(self):
        data = parse_activity({"activityId": 1, "startTimeLocal": "2026-09-20 07:30:00",
                               "distance": 9460.0, "duration": 3303.4, "averageSpeed": 2.864})
        self.assertEqual(data["avg_pace_sec_km"], 349)

    class W:
        def __init__(self, d, km=8.0): self.scheduled_date, self.target_distance_km = d, km

    def test_match_prefers_same_day_then_previous(self):
        W = self.W
        mon, tue, wed = W(date(2026, 9, 28)), W(date(2026, 9, 29)), W(date(2026, 9, 30))
        self.assertIs(match_workout([mon, tue, wed], date(2026, 9, 29)), tue)
        self.assertIs(match_workout([mon, wed], date(2026, 9, 29)), mon)
        self.assertIsNone(match_workout([mon], date(2026, 10, 1)))

    def test_match_ignores_short_runs(self):
        tue = self.W(date(2026, 9, 29), km=10.0)
        self.assertIsNone(match_workout([tue], date(2026, 9, 29), 3.0))  # warm-up or casual jog
        self.assertIs(match_workout([tue], date(2026, 9, 29), 6.0), tue)
        self.assertIs(match_workout([tue], date(2026, 9, 29), 0), tue)  # no distance (treadmill): not discarded

    def test_second_run_of_a_day_does_not_take_tomorrows_session(self):
        mon, tue = date(2026, 9, 28), self.W(date(2026, 9, 29))
        self.assertIsNone(match_workout([tue], mon, 8.0, busy_days={mon}))
        self.assertIs(match_workout([tue], mon, 8.0, busy_days=set()), tue)  # no session that day: it was run early


class ProposalRulesTest(unittest.TestCase):
    base = {"compliance": 0.95, "quality_dev": None, "easy_dev": None, "rpe_avg": 5}

    def run_rules(self, fatigue="good", pain="no", factor=1.0, **metrics):
        return propose({**self.base, **metrics}, fatigue, pain, 45.0, factor, True)

    def test_all_good_keeps_plan(self):
        p = self.run_rules()
        self.assertFalse(p["changes"])
        self.assertEqual(p["reasons"], [{"code": "all_good"}])

    def test_volume_rules(self):
        self.assertEqual(self.run_rules(fatigue="tired")["volume_to"], 0.93)
        self.assertEqual(self.run_rules(compliance=0.5)["volume_to"], 0.85)
        self.assertEqual(self.run_rules(fatigue="very_tired", factor=0.75)["volume_to"], 0.7)  # floor
        self.assertEqual(self.run_rules(factor=0.9)["volume_to"], 0.95)  # recovers
        self.assertEqual(self.run_rules(factor=0.98)["volume_to"], 1.0)  # ceiling

    def test_pain_forces_deload_and_blocks_vdot_increase(self):
        p = self.run_rules(pain="yes", quality_dev=0.08)
        self.assertTrue(p["deload_this_week"])
        self.assertEqual(p["vdot_to"], p["vdot_from"])

    def test_vdot_rules(self):
        self.assertEqual(self.run_rules(quality_dev=0.035)["vdot_to"], 45.5)
        self.assertEqual(self.run_rules(quality_dev=0.06)["vdot_to"], 46.0)
        self.assertEqual(self.run_rules(quality_dev=0.06, rpe_avg=8)["vdot_to"], 45.0)  # fast but very hard
        self.assertEqual(self.run_rules(quality_dev=-0.05, fatigue="tired")["vdot_to"], 44.5)
        self.assertEqual(self.run_rules(quality_dev=-0.05)["vdot_to"], 45.0)  # slow but fresh: no change

    def test_load_spike_cuts_volume_and_blocks_vdot_increase(self):
        p = self.run_rules(acwr=1.62, quality_dev=0.06)
        self.assertEqual(p["volume_to"], 0.9)
        self.assertEqual(p["vdot_to"], p["vdot_from"])
        self.assertEqual(p["reasons"][0], {"code": "load_spike", "ratio": 1.62})
        p = self.run_rules(acwr=1.4)
        self.assertFalse(p["changes"])
        self.assertEqual(p["tips"], [{"code": "load_high", "ratio": 1.4}])
        self.assertFalse(self.run_rules(acwr=1.1)["tips"])

    def test_form_gap_is_only_a_tip(self):
        p = self.run_rules(form_vdot=47.0)
        self.assertFalse(p["changes"])
        self.assertEqual(p["tips"], [{"code": "form_above", "form": 47.0, "vdot": 45.0}])
        self.assertEqual(self.run_rules(form_vdot=43.0)["tips"][0]["code"], "form_below")
        self.assertFalse(self.run_rules(form_vdot=46.0)["tips"])
        # If the review already changes the VDOT the tip is not repeated
        self.assertFalse(self.run_rules(form_vdot=47.0, quality_dev=0.06)["tips"])

    def test_easy_too_fast_is_a_tip_not_a_change(self):
        p = self.run_rules(easy_dev=0.08)
        self.assertEqual(p["tips"][0]["code"], "easy_too_fast")
        self.assertFalse(p["changes"])
        self.assertEqual(self.run_rules(easy_dev=0.08, easy_rpe=6.0)["tips"][0]["code"], "easy_too_fast")

    def test_fast_easy_but_slow_quality_means_aerobic_base_ahead(self):
        p = self.run_rules(easy_dev=0.09, easy_rpe=4.0, quality_mean=-0.04)
        self.assertEqual(p["tips"], [{"code": "aerobic_ahead", "pct": 9, "q": 4}])
        # Quality on pace: the low-VDOT tip remains
        self.assertEqual(self.run_rules(easy_dev=0.09, easy_rpe=4.0, quality_mean=0.0)["tips"][0]["code"],
                         "easy_comfortable")

    def test_fading_intervals_and_efficiency_trend_are_tips(self):
        p = self.run_rules(fade=0.055)
        self.assertEqual(p["tips"], [{"code": "fade", "pct": 6}])
        self.assertFalse(p["changes"])
        self.assertFalse(self.run_rules(fade=0.01)["tips"])
        self.assertEqual(self.run_rules(efficiency_change=4.2)["tips"], [{"code": "efficiency_up", "pct": 4.2}])
        self.assertEqual(self.run_rules(efficiency_change=-5.0)["tips"], [{"code": "efficiency_down", "pct": 5.0}])
        self.assertFalse(self.run_rules(efficiency_change=1.0)["tips"])

    def test_comfortable_fast_easy_runs_hint_low_vdot(self):
        p = self.run_rules(easy_dev=0.09, easy_rpe=4.0)
        self.assertEqual(p["tips"], [{"code": "easy_comfortable", "pct": 9, "rpe": 4.0, "vdot": 45.0}])
        self.assertFalse(p["changes"])
        # Comfortable but tired: still "you're going too fast"
        self.assertEqual(self.run_rules(easy_dev=0.09, easy_rpe=4.0, fatigue="tired")["tips"][0]["code"],
                         "easy_too_fast")
        # If the review already raises the VDOT the tip is not needed
        self.assertFalse(self.run_rules(easy_dev=0.09, easy_rpe=4.0, quality_dev=0.06)["tips"])


def structured_laps(rep_secs, rep_m=1000, step_split=1):
    """Laps of intervals run with the watch workout (warm-up split by auto-lap)."""
    laps = [{"type": "WARMUP", "m": 1000, "s": 390, "hr": 128, "step": 0},
            {"type": "WARMUP", "m": 500, "s": 200, "hr": 130, "step": 0}]
    step = 1
    for i, sec in enumerate(rep_secs):
        for _ in range(step_split):
            laps.append({"type": "ACTIVE", "m": rep_m / step_split, "s": sec / step_split, "hr": 150, "step": step})
        step += 1
        if i < len(rep_secs) - 1:
            laps.append({"type": "RECOVERY", "m": 260, "s": 120, "hr": 138, "step": step})
            step += 1
    laps += [{"type": "COOLDOWN", "m": 1500, "s": 600, "hr": 135, "step": step},
             {"type": "COOLDOWN", "m": 17, "s": 9, "hr": 140, "step": None}]
    return laps


class WorkLapsTest(unittest.TestCase):
    spec = {"kind": "intervals", "reps": 6, "dist_m": 1000, "rest_sec": 120}

    def test_work_blocks_exclude_warmup_and_recoveries(self):
        w = work_summary(structured_laps([320, 330, 340, 340, 345, 340]))
        self.assertEqual(len(w["blocks"]), 6)
        self.assertEqual(w["km"], 6.0)
        self.assertEqual(w["pace_sec_km"], 336)
        self.assertEqual(w["blocks"][0]["pace_sec_km"], 320)
        self.assertEqual(w["avg_hr"], 150)

    def test_auto_laps_split_one_step_into_one_block(self):
        w = work_summary(structured_laps([1500], rep_m=5000, step_split=5))  # 5 km tempo, lap per km
        self.assertEqual(len(w["blocks"]), 1)
        self.assertEqual(w["blocks"][0]["km"], 5.0)

    def test_fade_compares_last_third_with_first(self):
        w = work_summary(structured_laps([320, 330, 340, 340, 345, 340]))
        self.assertAlmostEqual(w["fade"], (342.5 - 325) / 325, places=3)
        self.assertEqual(work_summary(structured_laps([330] * 6))["fade"], 0.0)
        self.assertIsNone(work_summary(structured_laps([330, 330]))["fade"])  # too few blocks

    def test_grade_adjusted_pace_is_used_when_available(self):
        laps = structured_laps([330, 330, 330])
        for lap in laps:
            if lap["type"] == "ACTIVE":
                lap["gs"] = 315  # uphill: on flat ground it would have been faster
        w = work_summary(laps)
        self.assertEqual((w["pace_sec_km"], w["gap_sec_km"]), (330, 315))
        self.assertEqual(work_pace(w), 315)
        self.assertEqual(work_pace(work_summary(structured_laps([330] * 3))), 330)

    def test_free_run_without_structure_has_no_work_blocks(self):
        laps = [{"type": "ACTIVE", "m": 1000, "s": 330, "hr": 140, "step": None} for _ in range(8)]
        self.assertIsNone(work_summary(laps))
        self.assertIsNone(work_summary([]))

    def test_expected_work_pace_is_the_target_pace(self):
        self.assertAlmostEqual(expected_work_pace(self.spec, 40), calculate_training_paces(40)["interval_sec"], delta=1)
        tempo = {"kind": "tempo", "km": 4}
        self.assertAlmostEqual(expected_work_pace(tempo, 40), calculate_training_paces(40)["threshold_sec"], delta=1)
        self.assertEqual(expected_work_pace({"kind": "easy", "km": 8}, 40), 0.0)

    def test_session_vdot_from_work_blocks(self):
        pace = expected_work_pace(self.spec, 38)
        self.assertAlmostEqual(session_vdot(self.spec, pace, 36, work=True), 38, delta=0.2)
        # The same pace read as the whole-session average would give a very different VDOT
        self.assertNotAlmostEqual(session_vdot(self.spec, pace, 36) or 0, 38, delta=1)

    def test_work_band_needs_precision(self):
        self.assertEqual(pace_check("work", 322, 330)["level"], "ok")
        self.assertEqual(pace_check("work", 322, 335)["level"], "near")
        self.assertEqual(pace_check("work", 322, 350)["level"], "off")


class StatsTest(unittest.TestCase):
    def test_easy_runs_tolerate_slow_but_not_fast(self):
        self.assertEqual(pace_check("easy", 360, 390)["level"], "ok")  # 8% slower
        self.assertEqual(pace_check("easy", 360, 342)["level"], "ok")  # 5% faster: within the E range
        self.assertEqual(pace_check("easy", 360, 324)["level"], "near")  # 10% faster
        c = pace_check("easy", 360, 310)  # 14% faster
        self.assertEqual((c["level"], c["direction"]), ("off", "fast"))

    def test_fast_easy_run_is_ok_if_it_felt_comfortable(self):
        self.assertEqual(pace_check("long_run", 360, 310, rpe=4)["level"], "ok")
        self.assertEqual(pace_check("easy", 360, 310, rpe=6)["level"], "off")
        self.assertEqual(pace_check("tempo", 300, 270, rpe=3)["level"], "off")  # easy runs only

    def test_quality_needs_precision_and_race_never_too_fast(self):
        self.assertEqual(pace_check("tempo", 300, 306)["level"], "ok")
        self.assertEqual(pace_check("tempo", 300, 320)["level"], "near")
        self.assertEqual(pace_check("tempo", 300, 330)["level"], "off")
        self.assertEqual(pace_check("race", 300, 250)["level"], "ok")
        self.assertIsNone(pace_check("hills", 300, 300))  # by effort
        self.assertIsNone(pace_check("easy", 300, 0))

    def test_adherence_counts_only_resolved_sessions(self):
        s = lambda type, status, km, actual=None, pace=None: dict(type=type, status=status, planned_km=km,
                                                                  actual_km=actual, pace=pace)
        a = adherence([s("easy", "completed", 8, 8.4, "ok"), s("easy", "missed", 8),
                       s("tempo", "completed", 10, None, "near"), s("hills", "completed", 9, 9),
                       s("long_run", "scheduled", 16)])
        self.assertEqual(a["sessions"], {"done": 3, "total": 4, "pct": 75})
        self.assertEqual(a["km"], {"done": 27.4, "planned": 35, "pct": 78})
        self.assertEqual((a["pace"]["ok"], a["pace"]["checked"], a["pace"]["pct"]), (1, 2, 50))
        self.assertEqual([t["type"] for t in a["by_type"]], ["easy", "tempo", "hills"])
        self.assertEqual(a["by_type"][0], {"type": "easy", "done": 1, "total": 2, "pct": 50})
        self.assertIsNone(adherence([])["sessions"]["pct"])


class FormTest(unittest.TestCase):
    def test_session_vdot_inverts_expected_pace(self):
        from app.engine.workouts import expected_pace
        spec = {"kind": "tempo", "km": 5}
        pace = expected_pace(spec, 48.0)
        self.assertAlmostEqual(session_vdot(spec, pace, 45.0), 48.0, delta=0.15)
        self.assertIsNone(session_vdot(spec, expected_pace(spec, 56.0), 45.0))  # outlier
        self.assertIsNone(session_vdot(spec, 0, 45.0))

    def test_form_needs_three_recent_sessions(self):
        today = date(2026, 9, 24)
        pts = [(today - timedelta(days=d), v) for d, v in ((2, 47.0), (9, 46.0), (16, 49.0), (60, 30.0))]
        self.assertEqual(form_estimate(pts, today), {"vdot": 47.0, "sessions": 3})
        self.assertIsNone(form_estimate(pts[:2], today))


class AerobicTest(unittest.TestCase):
    def test_meters_per_beat(self):
        self.assertEqual(meters_per_beat(10, 3600, 140), 1.19)  # 166.7 m/min ÷ 140
        self.assertIsNone(meters_per_beat(10, 3600, None))
        self.assertIsNone(meters_per_beat(10, 3600, 60))  # unreliable heart rate

    def test_efficiency_trend(self):
        d0 = date(2026, 8, 1)
        pts = [(d0 + timedelta(days=7 * i), 1.10 + 0.01 * i) for i in range(8)]
        t = efficiency_trend(pts)
        self.assertEqual(len(t["series"]), 8)
        self.assertGreater(t["change_pct"], 0)
        self.assertIsNone(efficiency_trend(pts[:3])["change_pct"])

    def test_hard_fraction_follows_session_structure(self):
        self.assertEqual(hard_fraction({"kind": "easy", "km": 8}, 45), 0.0)
        self.assertEqual(hard_fraction({"kind": "race", "distance": "10k"}, 45), 1.0)
        tempo = hard_fraction({"kind": "tempo", "km": 5}, 45)
        self.assertTrue(0.4 < tempo < 0.7)

    def test_intensity_distribution(self):
        d = intensity_distribution([(60, 0.0, False), (60, 0.0, False), (50, 0.4, False), (30, 0.0, True)])
        self.assertEqual((d["easy_pct"], d["moderate_pct"], d["hard_pct"]), (75, 15, 10))
        self.assertTrue(d["balanced"])
        self.assertFalse(intensity_distribution([(40, 0.8, False), (40, 0.0, False)])["balanced"])
        self.assertIsNone(intensity_distribution([])["easy_pct"])


class LoadTest(unittest.TestCase):
    today = date(2026, 9, 24)

    def runs(self, weeks, per_week_load, days=(0, 2, 4, 6)):
        """Load spread over 4 days per week, ending today."""
        out = []
        for wk in range(weeks):
            load = per_week_load(wk) / len(days)
            for d in days:
                day = self.today - timedelta(days=7 * (weeks - 1 - wk) + (6 - d))
                out.append((day, load))
        return out

    def test_session_load_uses_default_effort(self):
        self.assertEqual(session_load(40, None, "easy"), 120)
        self.assertEqual(session_load(40, 8, "easy"), 320)
        self.assertEqual(session_load(40, None, None), 160)  # activity outside the plan

    def test_steady_training_is_optimal(self):
        s = load_status(self.runs(6, lambda wk: 1000), self.today, self.today - timedelta(days=41))
        self.assertAlmostEqual(s["ratio"], 1.0, places=2)
        self.assertEqual(s["zone"], "optimal")
        self.assertTrue(s["series"])

    def test_sudden_spike_is_high_risk(self):
        s = load_status(self.runs(6, lambda wk: 2000 if wk == 5 else 1000), self.today, self.today - timedelta(days=41))
        self.assertEqual(s["zone"], "high")
        s = load_status(self.runs(6, lambda wk: 400 if wk == 5 else 1000), self.today, self.today - timedelta(days=41))
        self.assertEqual(s["zone"], "low")

    def test_zone_limits_are_inclusive(self):
        from app.engine.stats import acwr_zone
        self.assertEqual([acwr_zone(r) for r in (0.79, 0.8, 1.3, 1.31, 1.5, 1.51)],
                         ["low", "optimal", "optimal", "caution", "caution", "high"])

    def test_needs_three_weeks_of_history(self):
        s = load_status(self.runs(2, lambda wk: 1000), self.today, self.today - timedelta(days=13))
        self.assertIsNone(s["ratio"])
        self.assertEqual(s["available_in_days"], 7)
        self.assertEqual(s["series"], [])


if __name__ == "__main__":
    unittest.main()
