"""
Session rendering.

Each session is stored as a minimal structure (spec), e.g.
    {"kind": "intervals", "reps": 5, "dist_m": 800, "rest_sec": 90}
and from it + VDOT + language the title, description, steps,
distance, duration and Garmin Connect payload are derived. This way a VDOT or
language change does not require translating or rewriting stored data.
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from app.engine.vdot import (
    DISTANCE_METERS, calculate_training_paces, pace_to_speed_ms,
    predict_race_time_range, seconds_to_time,
)

WARMUP_M = 1500.0
COOLDOWN_M = 1500.0

TEXT = {
    "es": {
        "easy": "Rodaje suave {km} km",
        "long_run": "Tirada larga {km} km",
        "tempo": "Tempo {km} km",
        "intervals": "Series {reps}x{dist}m",
        "hills": "Cuestas {reps}x{sec}s",
        "race": "Carrera {dist}",
        "easy_desc": "Ritmo conversacional, por sensaciones: debes poder hablar sin esfuerzo. El ritmo es solo orientativo.",
        "long_run_desc": "Ritmo suave y constante, por sensaciones. Construye resistencia; no la conviertas en una carrera.",
        "tempo_desc": "Calentamiento, {km} km a ritmo umbral (cómodamente duro) y vuelta a la calma.",
        "intervals_desc": "Calentamiento, {reps} series de {dist} m con {rest}s trotando entre series y vuelta a la calma.",
        "hills_desc": "Calentamiento, {reps} subidas de {sec}s (pendiente 5-8%) a esfuerzo fuerte, bajando al trote, y vuelta a la calma.",
        "race_desc": "Día de carrera. Sal controlado el primer kilómetro y ve de menos a más.",
        "race_b_desc": "Carrera de preparación: córrela fuerte si te encuentras bien. Tu tiempo sirve para ajustar los ritmos del plan.",
        "step_warmup": "Calentamiento suave",
        "step_cooldown": "Vuelta a la calma",
        "step_easy": "Ritmo suave",
        "step_long": "Ritmo suave y constante",
        "step_tempo": "Ritmo umbral",
        "step_interval": "Serie {i}/{n}",
        "step_recovery": "Trote de recuperación",
        "step_hill": "Subida fuerte {i}/{n}",
        "step_hill_down": "Bajada al trote",
        "step_race": "Ritmo de carrera",
    },
    "en": {
        "easy": "Easy run {km} km",
        "long_run": "Long run {km} km",
        "tempo": "Tempo {km} km",
        "intervals": "Intervals {reps}x{dist}m",
        "hills": "Hill repeats {reps}x{sec}s",
        "race": "Race {dist}",
        "easy_desc": "Conversational pace, run by feel: you should be able to talk comfortably. Pace is only a guide.",
        "long_run_desc": "Easy, steady pace, run by feel. Builds endurance; don't turn it into a race.",
        "tempo_desc": "Warm-up, {km} km at threshold pace (comfortably hard) and cool-down.",
        "intervals_desc": "Warm-up, {reps} x {dist} m with {rest}s jog recovery and cool-down.",
        "hills_desc": "Warm-up, {reps} x {sec}s uphill (5-8% grade) at hard effort, jog back down, and cool-down.",
        "race_desc": "Race day. Start controlled for the first kilometre and build from there.",
        "race_b_desc": "Tune-up race: run it hard if you feel good. Your time is used to adjust the plan's paces.",
        "step_warmup": "Easy warm-up",
        "step_cooldown": "Cool-down",
        "step_easy": "Easy pace",
        "step_long": "Easy, steady pace",
        "step_tempo": "Threshold pace",
        "step_interval": "Interval {i}/{n}",
        "step_recovery": "Recovery jog",
        "step_hill": "Hard uphill {i}/{n}",
        "step_hill_down": "Jog back down",
        "step_race": "Race pace",
    },
}

# Titles the app generates (or generated); used to avoid touching other workouts in Garmin
APP_TITLE_PATTERNS = [
    re.compile(r"^(rodaje suave|easy run|tirada larga|long run|tempo( run)?) [\d.]+ km", re.I),
    re.compile(r"^(series|intervals|cuestas|hill repeats) \d+x\d+[ms]\b", re.I),
    re.compile(r"^(carrera|race) (5k|10k|21k|42k)$", re.I),
]

_STEP_TYPES = {
    "warmup": (1, "warmup"),
    "cooldown": (2, "cooldown"),
    "interval": (3, "interval"),
    "recovery": (4, "recovery"),
}


def is_app_title(title: Optional[str]) -> bool:
    return bool(title) and any(p.match(title.strip()) for p in APP_TITLE_PATTERNS)


def _lang(lang: Optional[str]) -> Dict[str, str]:
    return TEXT.get((lang or "es").lower(), TEXT["es"])


def _fmt_km(km: float) -> str:
    return f"{km:.1f}".rstrip("0").rstrip(".")


def _step(kind: str, label: str, *, dist_m: float = 0, sec: float = 0,
          target: Optional[Tuple[int, int]] = None, ref: Optional[Tuple[int, int]] = None,
          est_pace: int = 0) -> Dict[str, Any]:
    """target = (slow pace, fast pace) in sec/km, sent to the watch; ref = guidance-only range
    (shown in the app, not on the watch); est_pace to estimate time/distance."""
    return {"kind": kind, "label": label, "dist_m": dist_m, "sec": sec, "target": target, "ref": ref,
            "est_pace": est_pace}


def build_steps(spec: Dict[str, Any], vdot: float, lang: str = "es") -> List[Dict[str, Any]]:
    tx = _lang(lang)
    p = calculate_training_paces(vdot)
    easy = (p["easy_max_sec"], p["easy_min_sec"])
    easy_mid = (easy[0] + easy[1]) // 2
    jog = int(p["easy_max_sec"] * 1.08)
    warmup = _step("warmup", tx["step_warmup"], dist_m=WARMUP_M, est_pace=easy_mid)
    cooldown = _step("cooldown", tx["step_cooldown"], dist_m=COOLDOWN_M, est_pace=easy_mid)
    kind = spec["kind"]

    if kind in ("easy", "long_run"):
        # Run by feel: no pace zone on the watch, the E range is kept as a reference
        label = tx["step_easy"] if kind == "easy" else tx["step_long"]
        return [_step("interval", label, dist_m=spec["km"] * 1000, ref=easy, est_pace=easy_mid)]

    if kind == "tempo":
        t = p["threshold_sec"]
        return [warmup,
                _step("interval", tx["step_tempo"], dist_m=spec["km"] * 1000, target=(t + 8, t - 8), est_pace=t),
                cooldown]

    if kind == "intervals":
        n, i_pace = spec["reps"], p["interval_sec"]
        steps = [warmup]
        for i in range(1, n + 1):
            steps.append(_step("interval", tx["step_interval"].format(i=i, n=n), dist_m=spec["dist_m"],
                               target=(i_pace + 6, i_pace - 6), est_pace=i_pace))
            if i < n:
                steps.append(_step("recovery", tx["step_recovery"], sec=spec["rest_sec"], est_pace=jog))
        return steps + [cooldown]

    if kind == "hills":
        n = spec["reps"]
        steps = [warmup]
        for i in range(1, n + 1):
            # Uphill, pace is not a useful reference: run by effort
            steps.append(_step("interval", tx["step_hill"].format(i=i, n=n), sec=spec["climb_sec"],
                               est_pace=int(p["interval_sec"] * 1.25)))
            steps.append(_step("recovery", tx["step_hill_down"], sec=spec["rest_sec"], est_pace=int(jog * 1.3)))
        return steps + [cooldown]

    if kind == "race":
        pace = predict_race_time_range(vdot, spec["distance"], spec.get("terrain", "flat"))["pace_sec_km"]
        return [_step("interval", tx["step_race"], dist_m=DISTANCE_METERS[spec["distance"]],
                      target=(pace + 5, pace - 5), est_pace=pace)]

    raise ValueError(f"Unknown session type: {kind}")


def _raw_totals(steps: List[Dict[str, Any]]) -> Tuple[float, float]:
    dist_m = 0.0
    secs = 0.0
    for s in steps:
        if s["dist_m"]:
            dist_m += s["dist_m"]
            secs += s["dist_m"] / 1000 * s["est_pace"]
        else:
            secs += s["sec"]
            dist_m += s["sec"] / s["est_pace"] * 1000 if s["est_pace"] else 0
    return dist_m, secs


def _totals(steps: List[Dict[str, Any]]) -> Tuple[float, int]:
    dist_m, secs = _raw_totals(steps)
    return round(dist_m / 1000, 1), int(round(secs / 60))


def expected_pace(spec: Dict[str, Any], vdot: float) -> float:
    """Expected average pace (sec/km) of the whole session, including warm-up and recoveries.
    Comparable with the average pace of the activity recorded in Garmin."""
    dist_m, secs = _raw_totals(build_steps(spec, vdot))
    return secs / (dist_m / 1000) if dist_m else 0.0


WORK_KINDS = ("tempo", "intervals")


def expected_work_pace(spec: Dict[str, Any], vdot: float) -> float:
    """Expected average pace (sec/km) of only the work blocks of a tempo or intervals
    (0 for other sessions). Comparable with the pace of the work laps recorded in Garmin."""
    if spec["kind"] not in WORK_KINDS:
        return 0.0
    work = [s for s in build_steps(spec, vdot) if s["kind"] == "interval" and s["dist_m"]]
    dist_km = sum(s["dist_m"] for s in work) / 1000
    return sum(s["dist_m"] / 1000 * s["est_pace"] for s in work) / dist_km if dist_km else 0.0


def title_and_description(spec: Dict[str, Any], lang: str = "es") -> Tuple[str, str]:
    tx = _lang(lang)
    kind = spec["kind"]
    if kind in ("easy", "long_run"):
        return tx[kind].format(km=_fmt_km(spec["km"])), tx[f"{kind}_desc"]
    if kind == "tempo":
        km = _fmt_km(spec["km"])
        return tx["tempo"].format(km=km), tx["tempo_desc"].format(km=km)
    if kind == "intervals":
        args = dict(reps=spec["reps"], dist=int(spec["dist_m"]), rest=int(spec["rest_sec"]))
        return tx["intervals"].format(**args), tx["intervals_desc"].format(**args)
    if kind == "hills":
        args = dict(reps=spec["reps"], sec=int(spec["climb_sec"]))
        return tx["hills"].format(**args), tx["hills_desc"].format(**args)
    if kind == "race":
        desc = tx["race_b_desc"] if spec.get("priority") == "b" else tx["race_desc"]
        return tx["race"].format(dist=spec["distance"].upper()), desc
    raise ValueError(f"Unknown session type: {kind}")


def render(spec: Dict[str, Any], vdot: float, lang: str = "es") -> Dict[str, Any]:
    """Full view of a session for the UI."""
    steps = build_steps(spec, vdot, lang)
    title, desc = title_and_description(spec, lang)
    km, minutes = _totals(steps)
    return {
        "title": title,
        "description": desc,
        "distance_km": km,
        "duration_min": minutes,
        "steps": [_ui_step(s) for s in steps],
    }


def summarize(spec: Dict[str, Any], vdot: float) -> Tuple[float, int]:
    """Estimated (km, minutes) of a session."""
    return _totals(build_steps(spec, vdot))


def _ui_step(s: Dict[str, Any]) -> Dict[str, Any]:
    if s["dist_m"]:
        d = s["dist_m"]
        duration = f"{_fmt_km(d / 1000)} km" if d >= 1000 else f"{int(d)} m"
    else:
        duration = seconds_to_time(int(s["sec"])) if s["sec"] >= 60 else f"{int(s['sec'])} s"
    pace = None
    if s["target"] or s["ref"]:
        slow, fast = s["target"] or s["ref"]
        pace = f"{'' if s['target'] else '~'}{seconds_to_time(fast)}–{seconds_to_time(slow)} /km"
    return {"kind": s["kind"], "label": s["label"], "duration": duration, "pace": pace}


def garmin_payload(spec: Dict[str, Any], vdot: float, lang: str = "es") -> Dict[str, Any]:
    """Payload for the Garmin Connect workout-service."""
    steps = build_steps(spec, vdot, lang)
    title, desc = title_and_description(spec, lang)
    running = {"sportTypeId": 1, "sportTypeKey": "running"}
    g_steps = []
    for order, s in enumerate(steps, start=1):
        type_id, type_key = _STEP_TYPES[s["kind"]]
        step = {
            "type": "ExecutableStepDTO",
            "stepOrder": order,
            "stepType": {"stepTypeId": type_id, "stepTypeKey": type_key},
            "description": s["label"],
        }
        if s["dist_m"]:
            step["endCondition"] = {"conditionTypeId": 3, "conditionTypeKey": "distance"}
            step["endConditionValue"] = float(s["dist_m"])
        else:
            step["endCondition"] = {"conditionTypeId": 2, "conditionTypeKey": "time"}
            step["endConditionValue"] = float(s["sec"])
        if s["target"]:
            slow, fast = s["target"]
            step["targetType"] = {"workoutTargetTypeId": 6, "workoutTargetTypeKey": "pace.zone"}
            step["targetValueOne"] = pace_to_speed_ms(slow)
            step["targetValueTwo"] = pace_to_speed_ms(fast)
        else:
            step["targetType"] = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target"}
        g_steps.append(step)

    return {
        "sportType": running,
        "workoutName": title[:64],
        "description": desc,
        "workoutSegments": [{"segmentOrder": 1, "sportType": running, "workoutSteps": g_steps}],
    }
