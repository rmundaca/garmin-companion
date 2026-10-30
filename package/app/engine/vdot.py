"""Daniels & Gilbert formulas: VDOT, training paces and race prediction."""
import math
from functools import lru_cache
from typing import Dict, Any

DISTANCE_METERS = {
    "5k": 5000.0,
    "10k": 10000.0,
    "21k": 21097.5,
    "42k": 42195.0,
}

# Plausible range: from ~5K in 75 min (10) to beyond the world record (~85)
VDOT_MIN = 10.0
VDOT_MAX = 90.0

# Time penalty for course elevation gain
TERRAIN_FACTORS = {
    "flat": 1.0,       # < 5 m/km
    "rolling": 1.012,  # < 7 m/km
    "moderate": 1.028, # 7-20 m/km
    "hilly": 1.050,    # > 20 m/km
}


def seconds_to_time(seconds: int, include_hours: bool = False) -> str:
    """Converts seconds to H:MM:SS or M:SS."""
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0 or include_hours:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _vo2_at(v_m_min: float) -> float:
    return -4.60 + 0.182258 * v_m_min + 0.000104 * v_m_min ** 2


def _sustainable_fraction(t_min: float) -> float:
    return 0.8 + 0.1894393 * math.exp(-0.012778 * t_min) + 0.2989558 * math.exp(-0.1932605 * t_min)


def calculate_vdot(distance_meters: float, time_seconds: float) -> float:
    t_min = time_seconds / 60.0
    return round(_vo2_at(distance_meters / t_min) / _sustainable_fraction(t_min), 2)


def get_vdot_from_race(distance_key: str, time_seconds: int) -> float:
    dist_m = DISTANCE_METERS.get((distance_key or "").lower())
    if not dist_m:
        raise ValueError(f"Unknown distance: {distance_key}")
    if time_seconds <= 0:
        raise ValueError("Time must be greater than zero")
    vdot = calculate_vdot(dist_m, time_seconds)
    if not VDOT_MIN <= vdot <= VDOT_MAX:
        raise ValueError("Result out of range")
    return vdot


def _pace_at_fraction(vdot: float, fraction: float) -> int:
    """Pace (sec/km) at which `fraction` of VDOT is used."""
    a, b, c = 0.000104, 0.182258, -(4.60 + fraction * vdot)
    v = (-b + math.sqrt(max(0.0, b * b - 4 * a * c))) / (2 * a)  # m/min
    return int(round(60000.0 / v)) if v > 0 else 0


@lru_cache(maxsize=64)
def _paces(vdot: float) -> tuple:
    return (
        _pace_at_fraction(vdot, 0.72),  # easy fast
        _pace_at_fraction(vdot, 0.62),  # easy slow
        _pace_at_fraction(vdot, 0.82),  # marathon
        _pace_at_fraction(vdot, 0.88),  # threshold
        _pace_at_fraction(vdot, 0.98),  # intervals
        _pace_at_fraction(vdot, 1.05),  # repetitions
    )


def calculate_training_paces(vdot: float) -> Dict[str, Any]:
    """Daniels paces in sec/km: E (62-72%), M (82%), T (88%), I (98%), R (105%)."""
    e_fast, e_slow, m, t, i, r = _paces(round(float(vdot), 2))
    return {
        "vdot": vdot,
        "easy_min_sec": e_fast,
        "easy_max_sec": e_slow,
        "marathon_sec": m,
        "threshold_sec": t,
        "interval_sec": i,
        "repetition_sec": r,
    }


def pace_to_speed_ms(pace_sec_km: float) -> float:
    return round(1000.0 / pace_sec_km, 3) if pace_sec_km > 0 else 0.0


def predict_race_time_range(vdot: float, target_distance: str, terrain: str = "flat") -> Dict[str, Any]:
    """Estimated time (optimistic -2% / conservative +3%) adjusted for elevation."""
    distance = (target_distance or "10k").lower()
    dist_m = DISTANCE_METERS.get(distance, 10000.0)

    low, high = 5.0, 600.0
    for _ in range(40):
        mid = (low + high) / 2.0
        if _vo2_at(dist_m / mid) / _sustainable_fraction(mid) < vdot:
            high = mid
        else:
            low = mid

    nominal = int(round(mid * 60.0 * TERRAIN_FACTORS.get((terrain or "flat").lower(), 1.0)))
    min_sec = int(round(nominal * 0.98))
    max_sec = int(round(nominal * 1.03))
    km = dist_m / 1000.0
    hours = nominal >= 3600
    return {
        "target_distance": distance,
        "vdot": round(vdot, 1),
        "nominal_sec": nominal,
        "min_sec": min_sec,
        "max_sec": max_sec,
        "pace_sec_km": int(round(nominal / km)),
        "formatted_nominal": seconds_to_time(nominal, hours),
        "formatted_range": f"{seconds_to_time(min_sec, hours)} – {seconds_to_time(max_sec, hours)}",
        "formatted_pace": f"{seconds_to_time(int(round(nominal / km)))} /km",
    }
