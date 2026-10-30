from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, UniqueConstraint, inspect
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    garmin_user_id = Column(String, unique=True, nullable=True)
    display_name = Column(String, nullable=True)
    reference_distance = Column(String, nullable=False, default="10k")  # 5k, 10k, 21k, 42k
    reference_time_sec = Column(Integer, nullable=False)
    calculated_vdot = Column(Float, nullable=False)
    preferred_language = Column(String, default="es")  # app and workout language
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plans = relationship("TrainingPlan", back_populates="user", cascade="all, delete-orphan")
    vdot_history = relationship("VdotHistory", cascade="all, delete-orphan", order_by="VdotHistory.recorded_on")
    garmin_deletions = relationship("GarminDeletion", cascade="all, delete-orphan")


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    target_distance = Column(String, nullable=False)  # 5k, 10k, 21k, 42k
    target_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    total_weeks = Column(Integer, nullable=False)
    weekly_days = Column(Text, nullable=False)  # JSON, 0=Monday ... 6=Sunday
    long_run_day = Column(Integer, nullable=False, default=6)
    terrain = Column(String, default="flat")  # flat, rolling, moderate, hilly
    running_level = Column(String, default="intermediate")  # beginner, intermediate, advanced, elite
    injury_history = Column(String, default="rarely_never")  # rarely_never, minor_past, frequent_recent
    vdot = Column(Float, nullable=True)  # current VDOT for future sessions
    predicted_time_min_sec = Column(Integer, nullable=True)
    predicted_time_max_sec = Column(Integer, nullable=True)
    status = Column(String, default="active")  # active, completed, cancelled
    adjust_json = Column(Text, nullable=True)  # accepted adjustments: {"volume_factor", "deload_weeks"}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserProfile", back_populates="plans")
    workouts = relationship("Workout", back_populates="plan", cascade="all, delete-orphan")
    reviews = relationship("PlanReview", back_populates="plan", cascade="all, delete-orphan")
    races = relationship("PlanRace", cascade="all, delete-orphan", order_by="PlanRace.race_date")


class PlanRace(Base):
    """B (tune-up) race within a plan. The goal race is TrainingPlan.target_date.
    Its session is a "race" Workout on that date; the result comes from its ActivityLog."""
    __tablename__ = "plan_races"
    __table_args__ = (UniqueConstraint("plan_id", "race_date"),)

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    race_date = Column(Date, nullable=False)
    distance = Column(String, nullable=False)  # 5k, 10k, 21k
    name = Column(String, nullable=True)
    vdot_decision = Column(String, nullable=True)  # applied, dismissed (post-race VDOT proposal)
    created_at = Column(DateTime, default=datetime.utcnow)


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday ... 6=Sunday
    scheduled_date = Column(Date, nullable=False)
    planned_date = Column(Date, nullable=True)  # original generator date (unchanged when moved)
    session_type = Column(String, nullable=False)  # easy, long_run, tempo, intervals, hills, race
    spec_json = Column(Text, nullable=True)  # session structure; title, steps and paces are derived from it
    vdot = Column(Float, nullable=True)  # VDOT used to compute this session's paces
    target_distance_km = Column(Float, nullable=True)
    estimated_duration_min = Column(Integer, nullable=True)
    garmin_workout_id = Column(String, nullable=True)
    garmin_schedule_id = Column(String, nullable=True)
    status = Column(String, default="scheduled")  # scheduled, completed, missed
    rpe = Column(Integer, nullable=True)  # perceived effort 1-10

    plan = relationship("TrainingPlan", back_populates="workouts")
    activity_log = relationship("ActivityLog", back_populates="workout", uselist=False)


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="SET NULL"), nullable=True)
    garmin_activity_id = Column(String, unique=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    activity_name = Column(String, nullable=True)
    actual_distance_km = Column(Float, nullable=False)
    actual_duration_sec = Column(Integer, nullable=False)
    avg_pace_sec_km = Column(Integer, nullable=False)
    avg_hr = Column(Integer, nullable=True)
    max_hr = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    user_rpe = Column(Integer, nullable=True)
    user_notes = Column(Text, nullable=True)
    # Garmin laps (quality sessions): [{"type", "m", "s", "hr", "step"}]; None = not read, [] = unavailable
    laps_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workout = relationship("Workout", back_populates="activity_log")


class PlanReview(Base):
    """Periodic plan review: period metrics, answers and adjustment proposal."""
    __tablename__ = "plan_reviews"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id", ondelete="CASCADE"), nullable=False)
    week_from = Column(Integer, nullable=False)
    week_to = Column(Integer, nullable=False)
    fatigue = Column(String, nullable=True)  # good, tired, very_tired
    pain = Column(String, nullable=True)  # no, mild, yes
    metrics_json = Column(Text, nullable=True)
    proposal_json = Column(Text, nullable=True)
    decision = Column(String, default="pending")  # pending, accepted, declined, skipped
    created_at = Column(DateTime, default=datetime.utcnow)
    decided_at = Column(DateTime, nullable=True)

    plan = relationship("TrainingPlan", back_populates="reviews")


class VdotHistory(Base):
    """Every change to the user's current VDOT: on plan creation, reference time change or accepted review."""
    __tablename__ = "vdot_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id", ondelete="SET NULL"), nullable=True)
    recorded_on = Column(Date, nullable=False)
    vdot = Column(Float, nullable=False)
    source = Column(String, nullable=False)  # plan, reference, review


class GarminDeletion(Base):
    """Workout to remove from Garmin. Kept until Garmin confirms the deletion,
    to retry on failure (expired session, network, rate limit)."""
    __tablename__ = "garmin_deletions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    garmin_workout_id = Column(String, nullable=True)
    garmin_schedule_id = Column(String, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


SCHEMA_VERSION = 2

# Columns each schema version stops using
_DROPPED = {
    # Stored paces, gender and pre-spec_json session fields
    1: {
        "user_profiles": ["pace_easy_min_sec", "pace_easy_max_sec", "pace_marathon_sec", "pace_threshold_sec",
                          "pace_interval_sec", "pace_repetition_sec"],
        "training_plans": ["gender"],
        "workouts": ["session_title", "description", "workout_steps_json"],
    },
    # Plan review is now always every 2 weeks
    2: {"training_plans": ["review_every_weeks"]},
}


def init_db_migrations(engine):
    """Migrations for existing databases, numbered with PRAGMA user_version (missing tables
    are created by create_all). Also applied to a copy restored from Settings.
    Each version drops its unused columns (DROP COLUMN, SQLite >= 3.35)."""
    with engine.begin() as conn:
        version = conn.exec_driver_sql("PRAGMA user_version").scalar()
        for target in range(version + 1, SCHEMA_VERSION + 1):
            for table, cols in _DROPPED[target].items():
                existing = {c["name"] for c in inspect(conn).get_columns(table)}
                for col in cols:
                    if col in existing:
                        conn.exec_driver_sql(f"ALTER TABLE {table} DROP COLUMN {col}")
        if version < SCHEMA_VERSION:
            conn.exec_driver_sql(f"PRAGMA user_version = {SCHEMA_VERSION}")
