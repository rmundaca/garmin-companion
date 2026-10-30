"""
Plan statistics (pure logic, no DB or network).

Pace compliance: the activity's actual average pace is compared with the expected average
pace of the whole session (`expected_pace`, which includes warm-up and recoveries).
The deviation is positive if the run was faster than planned. Each session type has
its band: on easy runs going slower is fine and going faster is only a problem if it was also hard
(with a comfortable RPE, running fast means the VDOT fell short, not a mistake); quality sessions aim for
precision; in a race going faster is never a mistake. Hills are run by effort and
are not evaluated.

Work blocks: if a tempo or intervals were run with the watch workout,
Garmin records one lap per step with its type (warm-up, work, recovery...). Then
only the pace of the work laps is compared with the target pace (T or I), without the
warm-up or rests diluting it. Without those laps the session's average pace is used.
If Garmin provides grade-adjusted pace, it is used (targets assume flat ground). With 3
or more blocks the fade is also measured: how much slower the last ones are than the first.

Adherence: completed sessions and km over already resolved sessions (done or
missed); pending ones do not count.

Estimated form: for each quality session (tempo, intervals, race) we find the VDOT at which
its expected pace matches the actual one (work blocks if present, otherwise the average). The median of recent sessions is the
"current form", comparable with the plan's current VDOT.

Aerobic efficiency: on easy and long runs with heart rate, meters covered per beat
(speed in m/min ÷ average HR). If it rises over time, you run more at the same cardiac cost.

Intensity distribution (80/20): easy, moderate and hard minutes over recent weeks.
In quality sessions the hard part comes from their structure (work blocks versus
warm-up and recoveries); easy runs run clearly too fast count as moderate.

Load (ACWR): session load = minutes × perceived effort (Foster's sRPE). The
acute:chronic ratio compares the load of the last 7 days with the weekly average of the last
4 weeks. With less than 3 weeks of history the chronic load is unreliable and is not computed.
"""
import math
from datetime import date, timedelta
from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Tuple

from app.engine.vdot import VDOT_MAX, VDOT_MIN
from app.engine.workouts import build_steps, expected_pace, expected_work_pace

INF = float("inf")

# type: (in range fast, in range slow, off fast, off slow) as a fraction of the expected pace;
# between "in range" and "off" the session is "near".
# On easy runs the expected pace is the center of the E range; its fast end is ~6 % above.
PACE_BANDS = {
    "easy": (0.06, 0.10, 0.12, 0.15),
    "long_run": (0.06, 0.10, 0.12, 0.15),
    "tempo": (0.03, 0.04, 0.06, 0.08),
    # The average pace includes rests between reps (sometimes standing): more margin on the slow side
    "intervals": (0.04, 0.06, 0.08, 0.12),
    "race": (INF, 0.03, INF, 0.06),
    # Work blocks only (tempo or intervals): with no rests, aim for precision
    "work": (0.03, 0.03, 0.06, 0.06),
}

TYPE_ORDER = ("easy", "long_run", "tempo", "intervals", "hills", "race")
EASY_TYPES = ("easy", "long_run")
# Max average RPE at which an easy run is considered comfortable (1-10 scale)
EASY_COMFORT_RPE = 4.5


def pace_check(session_type: str, expected_sec_km: float, actual_sec_km: float,
               rpe: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Pace verdict for a completed session: level = ok | near | off."""
    band = PACE_BANDS.get(session_type)
    if not band or not expected_sec_km or not actual_sec_km:
        return None
    dev = (expected_sec_km - actual_sec_km) / expected_sec_km
    ok_fast, ok_slow, off_fast, off_slow = band
    if -ok_slow <= dev <= ok_fast:
        level = "ok"
    elif -off_slow <= dev <= off_fast:
        level = "near"
    else:
        level = "off"
    if session_type in EASY_TYPES and dev > 0 and rpe is not None and rpe <= EASY_COMFORT_RPE:
        level = "ok"  # fast but comfortable: run by feel
    return {
        "expected_sec_km": int(round(expected_sec_km)),
        "actual_sec_km": int(actual_sec_km),
        "deviation": round(dev, 3),
        "direction": "fast" if dev > 0 else "slow",
        "level": level,
    }


# --- Work blocks ----------------------------------------------------------------------

WORK_LAP_TYPES = ("ACTIVE", "INTERVAL")
STRUCTURE_LAP_TYPES = ("WARMUP", "RECOVERY", "REST", "COOLDOWN")
MIN_WORK_LAP_M = 100  # shorter laps: leftovers when stopping the watch
FADE_MIN_BLOCKS = 3


def work_pace(work: Dict[str, Any]) -> int:
    """Pace used to evaluate blocks: grade-adjusted if available."""
    return work.get("gap_sec_km") or work["pace_sec_km"]


def work_summary(laps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Pace, grade-adjusted pace, blocks (reps) and fade of the work laps,
    or None if the activity was not run with the structured workout (without
    warm-up/recovery laps, all laps are auto laps and work cannot be told apart).
    fade > 0: the last third of the blocks was slower than the first (fraction)."""
    if not any(lap.get("type") in STRUCTURE_LAP_TYPES for lap in laps):
        return None
    work = [lap for lap in laps if lap.get("type") in WORK_LAP_TYPES
            and (lap.get("m") or 0) >= MIN_WORK_LAP_M and lap.get("s")]
    if not work:
        return None
    # A long step may be split into several auto laps (e.g. a tempo, per km)
    blocks: List[List[Dict[str, Any]]] = []
    for lap in work:
        if blocks and lap.get("step") is not None and blocks[-1][-1].get("step") == lap.get("step"):
            blocks[-1].append(lap)
        else:
            blocks.append([lap])

    def summary(group):
        m, s = sum(x["m"] for x in group), sum(x["s"] for x in group)
        hr_s = sum(x["s"] for x in group if x.get("hr"))
        hr = round(sum(x["hr"] * x["s"] for x in group if x.get("hr")) / hr_s) if hr_s else None
        gap = round(sum(x["gs"] * x["m"] for x in group) / m) if all(x.get("gs") for x in group) else None
        return {"km": round(m / 1000, 2), "sec": round(s), "pace_sec_km": round(s / (m / 1000)),
                "gap_sec_km": gap, "avg_hr": hr}

    summaries = [summary(b) for b in blocks]
    fade = None
    if len(summaries) >= FADE_MIN_BLOCKS:
        k = math.ceil(len(summaries) / 3)
        first = mean(work_pace(b) for b in summaries[:k])
        last = mean(work_pace(b) for b in summaries[-k:])
        fade = round((last - first) / first, 3)
    return {**summary(work), "blocks": summaries, "fade": fade}


def _pct(a: float, b: float) -> Optional[int]:
    return int(round(100 * a / b)) if b else None


def adherence(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """sessions: dicts with type, status, planned_km, actual_km (or None) and pace (level or None)."""
    resolved = [s for s in sessions if s["status"] in ("completed", "missed")]
    done = [s for s in resolved if s["status"] == "completed"]

    km_planned = sum(s["planned_km"] or 0 for s in resolved)
    km_done = sum(s["actual_km"] if s["actual_km"] is not None else (s["planned_km"] or 0) for s in done)

    levels = [s["pace"] for s in done if s["pace"]]
    ok = levels.count("ok")

    by_type = []
    for kind in TYPE_ORDER:
        total = sum(1 for s in resolved if s["type"] == kind)
        if total:
            n = sum(1 for s in done if s["type"] == kind)
            by_type.append({"type": kind, "done": n, "total": total, "pct": _pct(n, total)})

    return {
        "sessions": {"done": len(done), "total": len(resolved), "pct": _pct(len(done), len(resolved))},
        "km": {"done": round(km_done, 1), "planned": round(km_planned, 1), "pct": _pct(km_done, km_planned)},
        "pace": {"ok": ok, "near": levels.count("near"), "off": levels.count("off"),
                 "checked": len(levels), "pct": _pct(ok, len(levels))},
        "by_type": by_type,
    }


# --- Load ------------------------------------------------------------------------

# Typical effort (1-10) when the user did not provide it
DEFAULT_RPE = {"easy": 3, "long_run": 4, "tempo": 6, "intervals": 7, "hills": 7, "race": 9}
UNPLANNED_RPE = 4
ACUTE_DAYS, CHRONIC_DAYS, MIN_HISTORY_DAYS = 7, 28, 21
ACWR_LOW, ACWR_HIGH, ACWR_SPIKE = 0.8, 1.3, 1.5  # optimal zone 0.8–1.3 (inclusive)


def session_load(minutes: float, rpe: Optional[int], session_type: Optional[str]) -> float:
    effort = rpe or (DEFAULT_RPE.get(session_type, UNPLANNED_RPE) if session_type else UNPLANNED_RPE)
    return max(0.0, minutes) * effort


def acwr_zone(ratio: float) -> str:
    if ratio < ACWR_LOW:
        return "low"
    if ratio <= ACWR_HIGH:
        return "optimal"
    return "caution" if ratio <= ACWR_SPIKE else "high"


def _daily(entries: Iterable[Tuple[date, float]]) -> Dict[date, float]:
    daily: Dict[date, float] = {}
    for day, load in entries:
        daily[day] = daily.get(day, 0.0) + load
    return daily


def _window(daily: Dict[date, float], end: date, days: int) -> float:
    return sum(daily.get(end - timedelta(days=i), 0.0) for i in range(days))


def _ratio_at(daily: Dict[date, float], day: date, history_start: date) -> Optional[Tuple[float, float, float]]:
    """(ratio, acute, weekly chronic) on a day, or None if history is missing or there is no chronic load."""
    available = (day - history_start).days + 1
    if available < MIN_HISTORY_DAYS:
        return None
    span = min(CHRONIC_DAYS, available)
    chronic = _window(daily, day, span) / (span / 7)
    if chronic <= 0:
        return None
    acute = _window(daily, day, ACUTE_DAYS)
    return acute / chronic, acute, chronic


def load_status(entries: List[Tuple[date, float]], today: date, history_start: date,
                series_days: int = 56) -> Dict[str, Any]:
    """Current load status and daily ratio series for the chart."""
    daily = _daily(entries)
    now = _ratio_at(daily, today, history_start)
    series = []
    for i in range(series_days - 1, -1, -1):
        day = today - timedelta(days=i)
        r = _ratio_at(daily, day, history_start)
        if r:
            series.append({"date": day.isoformat(), "ratio": round(r[0], 2)})
    status: Dict[str, Any] = {
        "ratio": None, "zone": None, "acute": None, "chronic": None, "series": series,
        "available_in_days": max(0, MIN_HISTORY_DAYS - ((today - history_start).days + 1)),
    }
    if now:
        ratio, acute, chronic = now
        ratio = round(ratio, 2)  # the zone is decided with the same value that is displayed
        status.update(ratio=ratio, zone=acwr_zone(ratio), acute=round(acute), chronic=round(chronic))
    return status


# --- Estimated form ------------------------------------------------------------------

FORM_TYPES = ("tempo", "intervals", "race")
FORM_WINDOW_DAYS = 42
FORM_MIN_SESSIONS = 3
FORM_MAX_GAP = 6.0  # further from the current VDOT is considered an outlier (GPS, stops, cut-short session)


def session_vdot(spec: Dict[str, Any], actual_sec_km: float, reference_vdot: float,
                 work: bool = False) -> Optional[float]:
    """VDOT at which the session's expected pace would equal the actual pace (None if an outlier).
    work=True compares only the work blocks; otherwise the average pace of the whole session."""
    if not actual_sec_km:
        return None
    pace = expected_work_pace if work else expected_pace
    lo, hi = VDOT_MIN, VDOT_MAX
    if actual_sec_km >= pace(spec, lo) or actual_sec_km <= pace(spec, hi):
        return None
    for _ in range(25):  # the expected pace drops (faster) as VDOT rises
        mid = (lo + hi) / 2
        if pace(spec, mid) > actual_sec_km:
            lo = mid
        else:
            hi = mid
    vdot = (lo + hi) / 2
    return round(vdot, 1) if abs(vdot - reference_vdot) <= FORM_MAX_GAP else None


def form_estimate(points: List[Tuple[date, float]], today: date) -> Optional[Dict[str, Any]]:
    """Median of per-session VDOTs over the last 6 weeks (min. 3 sessions)."""
    recent = [v for d, v in points if (today - d).days < FORM_WINDOW_DAYS]
    if len(recent) < FORM_MIN_SESSIONS:
        return None
    return {"vdot": round(median(recent), 1), "sessions": len(recent)}


# --- Aerobic efficiency -----------------------------------------------------------

EFFICIENCY_TYPES = ("easy", "long_run")
EFFICIENCY_MIN_POINTS = 4
EFFICIENCY_TREND_POINTS = 5  # moving average
MIN_EASY_HR, MAX_EASY_HR = 90, 200  # outside this range the average HR is unreliable


def meters_per_beat(distance_km: float, duration_sec: float, avg_hr: Optional[int]) -> Optional[float]:
    if not (distance_km and duration_sec and avg_hr) or not MIN_EASY_HR <= avg_hr <= MAX_EASY_HR:
        return None
    return round((distance_km * 1000 / (duration_sec / 60)) / avg_hr, 3)


def efficiency_trend(points: List[Tuple[date, float]]) -> Dict[str, Any]:
    """Series with moving average and change from start to end (averages of the first and last points)."""
    points = sorted(points)
    series = []
    for i, (d, v) in enumerate(points):
        window = [p[1] for p in points[max(0, i - EFFICIENCY_TREND_POINTS + 1):i + 1]]
        series.append({"date": d.isoformat(), "value": v, "trend": round(sum(window) / len(window), 3)})
    change = None
    if len(points) >= EFFICIENCY_MIN_POINTS:
        n = max(2, min(EFFICIENCY_TREND_POINTS, len(points) // 2))
        first = sum(p[1] for p in points[:n]) / n
        last = sum(p[1] for p in points[-n:]) / n
        change = round(100 * (last - first) / first, 1)
    return {"series": series, "change_pct": change, "latest": series[-1]["trend"] if series else None}


# --- Intensity distribution ---------------------------------------------------------

INTENSITY_WINDOW_DAYS = 28
EASY_TARGET_PCT = 75  # below this, too much intensity (ideal is around 80 %)
HARD_KINDS = ("tempo", "intervals", "hills", "race")


def hard_fraction(spec: Dict[str, Any], vdot: float) -> float:
    """Fraction of session time in work blocks (0 on easy runs)."""
    if spec["kind"] not in HARD_KINDS:
        return 0.0
    total = hard = 0.0
    for step in build_steps(spec, vdot):
        secs = step["sec"] or (step["dist_m"] / 1000 * step["est_pace"])
        total += secs
        if step["kind"] == "interval":
            hard += secs
    return hard / total if total else 0.0


def intensity_distribution(entries: List[Tuple[float, float, bool]]) -> Dict[str, Any]:
    """entries: (minutes, hard fraction, easy run too fast)."""
    easy = moderate = hard = 0.0
    for minutes, frac, too_fast in entries:
        if too_fast:
            moderate += minutes
        else:
            hard += minutes * frac
            easy += minutes * (1 - frac)
    total = easy + moderate + hard
    if not total:
        return {"minutes": 0, "easy_pct": None, "moderate_pct": None, "hard_pct": None, "balanced": None}
    pcts = [round(100 * x / total) for x in (easy, moderate, hard)]
    pcts[0] = 100 - pcts[1] - pcts[2]  # make them add up to 100
    return {"minutes": round(total), "easy_pct": pcts[0], "moderate_pct": pcts[1], "hard_pct": pcts[2],
            "balanced": pcts[0] >= EASY_TARGET_PCT}
