import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.plan_service import run_cycle

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler()


def start_scheduler():
    # Every hour, with a first run shortly after startup
    scheduler.add_job(run_cycle, "interval", minutes=60, id="garmin_cycle", replace_existing=True,
                      next_run_time=datetime.now() + timedelta(minutes=1), max_instances=1, coalesce=True)
    scheduler.start()
    logger.info("APScheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
