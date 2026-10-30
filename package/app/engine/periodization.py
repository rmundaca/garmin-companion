"""
Plan generation.

Weeks run Monday to Sunday: week 1 contains the start date and the last one
contains the race. Phases: base → build → peak → taper → race, with deload
weeks interspersed. Each session is returned as a spec (see engine/workouts.py).

B races: tune-up races within the plan. Their week ("tuneup") acts as a deload,
the preceding days have no quality work (rest the day before) and after the race there are a few
recovery days with easy runs only.
"""
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

MIN_WEEKS = 4
MAX_WEEKS = 30

DURATION_MATRIX = {
    "5k": {"beginner": (8, 12, 10), "intermediate": (6, 10, 8), "advanced": (6, 8, 8), "elite": (4, 8, 6)},
    "10k": {"beginner": (10, 14, 12), "intermediate": (8, 12, 10), "advanced": (8, 10, 8), "elite": (6, 10, 8)},
    "21k": {"beginner": (14, 18, 16), "intermediate": (12, 16, 14), "advanced": (10, 14, 12), "elite": (8, 12, 10)},
    "42k": {"beginner": (18, 24, 20), "intermediate": (16, 20, 18), "advanced": (14, 18, 16), "elite": (12, 16, 14)},
}

# (start, peak) of the long run in km and maximum weekly increase
LONG_RUN = {"5k": (5.0, 9.0, 1.0), "10k": (7.0, 14.0, 1.5), "21k": (10.0, 19.0, 2.0), "42k": (16.0, 32.0, 2.0)}
TEMPO_KM = {"5k": (3.0, 5.0), "10k": (3.0, 6.0), "21k": (4.0, 8.0), "42k": (5.0, 10.0)}
EASY_KM = {"beginner": 5.0, "intermediate": 6.0, "advanced": 7.0, "elite": 8.0}
HILL_MAX_REPS = {"rolling": 7, "moderate": 8, "hilly": 10}

B_DISTANCES = ("5k", "10k", "21k")
B_SHARPEN_DAYS = 3  # days before a B race without quality work (rest the day before)
B_RECOVERY_DAYS = {"5k": 2, "10k": 3, "21k": 6}  # days after with easy runs only
B_MIN_GAP_DAYS = 14  # minimum gap between B races


def get_duration_recommendation(distance: str, level: str = "intermediate",
                                injury: str = "rarely_never") -> Dict[str, int]:
    by_level = DURATION_MATRIX.get(distance, DURATION_MATRIX["10k"])
    lo, hi, rec = by_level.get(level, by_level["intermediate"])
    if injury == "frequent_recent":
        lo, hi, rec = lo + 2, hi + 4, rec + 2
    elif injury == "minor_past" and level == "beginner":
        hi, rec = hi + 2, rec + 1
    return {"min": lo, "max": hi, "recommended": rec}


def week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def count_weeks(start: date, race: date) -> int:
    return (week_monday(race) - week_monday(start)).days // 7 + 1


def week_of(start: date, d: date) -> int:
    return (week_monday(d) - week_monday(start)).days // 7 + 1


def taper_weeks(distance: str, total_weeks: int) -> int:
    """Taper weeks before race week."""
    return 2 if distance in ("21k", "42k") and total_weeks >= 10 else 1


def last_training_week(total_weeks: int, distance: str) -> int:
    """Last training week before the taper."""
    return total_weeks - 1 - taper_weeks(distance, total_weeks)


def week_phases(total_weeks: int, distance: str, injury: str = "rarely_never",
                extra_deload_weeks: Iterable[int] = (), tuneup_weeks: Iterable[int] = ()) -> List[str]:
    """Phase of each week: base, build, peak, deload, tuneup, taper or race.
    extra_deload_weeks: deloads added by the plan review.
    tuneup_weeks: weeks with a B race; they act as deloads, so a cycle deload falling
    right before or after is skipped to avoid two easy weeks in a row."""
    last_training = last_training_week(total_weeks, distance)
    base_end = max(1, round(last_training * 0.3))
    peak_start = max(base_end + 1, last_training - 2)
    cycle = 3 if injury == "frequent_recent" else 4
    extra = set(extra_deload_weeks)
    tuneup = set(tuneup_weeks)
    phases = []
    for w in range(1, total_weeks + 1):
        cycle_deload = w % cycle == 0 and not {w - 1, w + 1} & tuneup
        if w == total_weeks:
            phases.append("race")
        elif w > last_training:
            phases.append("taper")
        elif w in tuneup:
            phases.append("tuneup")
        elif (cycle_deload or w in extra) and w < last_training:
            phases.append("deload")
        elif w <= base_end:
            phases.append("base")
        elif w >= peak_start:
            phases.append("peak")
        else:
            phases.append("build")
    return phases


def b_race_error(start: date, target: date, distance: str, b_date: date, b_distance: str,
                 other_dates: Iterable[date] = ()) -> Optional[str]:
    """Error code if the B race does not fit the plan (None if valid): it must fall between
    week 2 and the last training week (before the taper) and away from other B races."""
    if b_distance not in B_DISTANCES:
        return "invalid_params"
    if b_date < start or week_of(start, b_date) < 2:
        return "b_race_too_early"
    if week_of(start, b_date) > last_training_week(count_weeks(start, target), distance):
        return "b_race_too_late"
    if any(abs((b_date - d).days) < B_MIN_GAP_DAYS for d in other_dates):
        return "b_race_too_close"
    return None


def tuneup_weeks(start: date, b_races: Iterable[Tuple[date, str]]) -> Dict[int, str]:
    """Week of each B race → its distance."""
    return {week_of(start, d): dist for d, dist in b_races}


def _near_b_race(d: date, b_races: Iterable[Tuple[date, str]]) -> Optional[Tuple[int, str]]:
    """(days relative to the B race, distance) if the day falls in its sharpening or recovery window."""
    for b, dist in b_races:
        offset = (d - b).days
        if -B_SHARPEN_DAYS <= offset <= B_RECOVERY_DAYS[dist]:
            return offset, dist
    return None


def _circular_gap(a: int, b: int) -> int:
    d = abs(a - b) % 7
    return min(d, 7 - d)


def assign_days(run_days: List[int], long_run_day: int) -> Dict[int, str]:
    """Role of each day: long, q1 (main quality), q2 (tempo) or easy.
    Quality is placed as far as possible from the long run and from the other quality session."""
    days = sorted(set(run_days) | {long_run_day})
    roles = {long_run_day: "long"}
    others = [d for d in days if d != long_run_day]
    hard = [long_run_day]
    slots = ["q1", "q2"] if len(others) >= 3 else ["q1"]
    for slot in slots:
        if not others:
            break
        best = max(others, key=lambda d: (min(_circular_gap(d, h) for h in hard), -d))
        roles[best] = slot
        hard.append(best)
        others.remove(best)
    for i, d in enumerate(others):
        roles[d] = "easy" if i == 0 else "easy_short"
    return roles


def _long_run_km(distance: str, level: str, progress_weeks: int, idx: int, volume: float) -> float:
    start, peak, max_step = LONG_RUN[distance]
    if level == "beginner":
        start, peak = max(4.0, start * 0.85), peak * 0.88
    elif level in ("advanced", "elite"):
        start, peak = start * 1.15, peak * 1.10
    step = min(max_step, (peak - start) / max(1, progress_weeks - 1))
    return round(min(peak, start + step * idx) * volume, 1)


def generate_plan(
    target_distance: str,
    start_date: date,
    target_date: date,
    weekly_days: List[int],
    long_run_day: int,
    terrain: str = "flat",
    running_level: str = "intermediate",
    injury_history: str = "rarely_never",
    volume_factor: float = 1.0,
    extra_deload_weeks: Iterable[int] = (),
    b_races: Iterable[Tuple[date, str]] = (),
) -> List[Dict[str, Any]]:
    """Returns [{week_number, scheduled_date, session_type, spec}] sorted by date.
    volume_factor and extra_deload_weeks are the adjustments accepted in reviews.
    b_races: [(date, distance)] of the B races (validated with b_race_error)."""
    distance = target_distance.lower()
    total = count_weeks(start_date, target_date)
    b_races = [(d, dist) for d, dist in b_races if start_date <= d < target_date]
    tuneups = tuneup_weeks(start_date, b_races)
    phases = week_phases(total, distance, injury_history, extra_deload_weeks, tuneups)
    roles = assign_days(weekly_days, long_run_day)
    has_hills = terrain in HILL_MAX_REPS
    volume = (0.9 if injury_history == "frequent_recent" else 1.0) * volume_factor
    easy_base = EASY_KM.get(running_level, 6.0) * volume

    training_weeks = [w for w, ph in enumerate(phases, start=1) if ph in ("base", "build", "peak", "deload", "tuneup")]
    last_training = training_weeks[-1] if training_weeks else 1
    long_peak = _long_run_km(distance, running_level, last_training, last_training - 1, volume)

    b_dates = {d for d, _ in b_races}
    shakeout_km = 4.0 if running_level != "beginner" else 3.0
    sessions = []
    monday0 = week_monday(start_date)
    for w, phase in enumerate(phases, start=1):
        progress = (w - 1) / max(1, last_training - 1) if phase not in ("taper", "race") else 1.0
        monday = monday0 + timedelta(weeks=w - 1)
        for day, role in sorted(roles.items()):
            d = monday + timedelta(days=day)
            if d < start_date or d > target_date:
                continue
            if phase == "race":
                if d == target_date:
                    continue  # race day is added below
                if (target_date - d).days <= 1:
                    continue  # rest the day before
                spec = {"kind": "easy", "km": shakeout_km}
            elif d in b_dates:
                continue  # the B race is added below
            else:
                # A B race week is trained as a deload; if the race is 10 km or
                # longer, it serves as the week's long run
                if phase == "tuneup" and role == "long" and tuneups[w] != "5k":
                    role = "easy"
                spec = _session_for(role, "deload" if phase == "tuneup" else phase, w, progress, distance,
                                    running_level, has_hills, terrain, easy_base, long_peak, volume,
                                    last_training)
                near = _near_b_race(d, b_races)
                if near:
                    spec = _around_b_race(spec, near, easy_base, shakeout_km)
                    if spec is None:
                        continue
            sessions.append({"week_number": w, "scheduled_date": d, "session_type": spec["kind"], "spec": spec})

    for d, dist in b_races:
        sessions.append({
            "week_number": week_of(start_date, d),
            "scheduled_date": d,
            "session_type": "race",
            "spec": {"kind": "race", "distance": dist, "terrain": "flat", "priority": "b"},
        })

    sessions.append({
        "week_number": total,
        "scheduled_date": target_date,
        "session_type": "race",
        "spec": {"kind": "race", "distance": distance, "terrain": terrain},
    })
    sessions.sort(key=lambda s: s["scheduled_date"])
    return sessions


def _around_b_race(spec: Dict[str, Any], near: Tuple[int, str], easy_base: float,
                   shakeout_km: float) -> Optional[Dict[str, Any]]:
    """Adjusts the session of a day near a B race (None: rest day).
    Before: no quality work and rest the day before. After: easy runs only; after a half marathon,
    rest the next day."""
    offset, dist = near
    if offset == -1 or (offset == 1 and dist == "21k"):
        return None
    if offset == 1:
        return {"kind": "easy", "km": shakeout_km}
    if spec["kind"] == "easy":
        return spec
    return {"kind": "easy", "km": round(max(3.0, easy_base * 0.8), 1)}


def _session_for(role, phase, week, progress, distance, level, has_hills, terrain,
                 easy_base, long_peak, volume, last_training) -> Dict[str, Any]:
    short = distance in ("5k", "10k")

    if role == "long":
        if phase == "taper":
            return {"kind": "long_run", "km": round(long_peak * 0.65, 1)}
        km = _long_run_km(distance, level, last_training, week - 1, volume)
        if phase == "deload":
            km = round(km * 0.75, 1)
        return {"kind": "long_run", "km": km}

    if role in ("easy", "easy_short"):
        km = easy_base * (1 + 0.25 * progress)
        if role == "easy_short":
            km -= 1.0
        if phase in ("deload", "taper"):
            km *= 0.8
        return {"kind": "easy", "km": round(max(3.0, km), 1)}

    t_lo, t_hi = TEMPO_KM[distance]
    tempo_km = round((t_lo + (t_hi - t_lo) * progress) * volume, 1)
    reps = lambda lo, hi: max(3, int(round((lo + (hi - lo) * progress) * volume)))

    if role == "q2":
        if phase in ("deload", "taper"):
            return {"kind": "easy", "km": round(easy_base * 0.8, 1)}
        return {"kind": "tempo", "km": tempo_km}

    # q1: main quality session by phase
    if phase == "deload":
        return {"kind": "tempo", "km": t_lo}
    if phase == "taper":
        if short:
            return {"kind": "intervals", "reps": 4, "dist_m": 400, "rest_sec": 60}
        return {"kind": "intervals", "reps": 3, "dist_m": 1000, "rest_sec": 90}
    hills_every = 3 if terrain == "rolling" else 2
    if has_hills and (phase == "base" or week % hills_every == 1):
        max_reps = HILL_MAX_REPS[terrain]
        climb = 45 if phase == "base" else (75 if terrain == "hilly" else 60)
        return {"kind": "hills", "reps": reps(4, max_reps),
                "climb_sec": climb, "rest_sec": int(climb * 1.5)}
    if phase == "base":
        return {"kind": "tempo", "km": t_lo}
    if short:
        dist_m = 800 if phase == "peak" else (600 if week % 2 else 800)
        return {"kind": "intervals", "reps": reps(4, 7), "dist_m": dist_m, "rest_sec": 90}
    return {"kind": "intervals", "reps": reps(3, 6), "dist_m": 1000, "rest_sec": 120}
