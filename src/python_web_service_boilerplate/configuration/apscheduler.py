from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
from tzlocal import get_localzone

from python_web_service_boilerplate.common.common_function import get_cpu_count
from python_web_service_boilerplate.common.profiling import elapsed_time
from python_web_service_boilerplate.configuration.database import sync_engine

# https://apscheduler.readthedocs.io/en/3.x/userguide.html#configuring-the-scheduler
# https://crontab.guru/

jobstores = {"default": SQLAlchemyJobStore(engine=sync_engine)}
executors = {"default": ThreadPoolExecutor(max_workers=get_cpu_count() * 2)}
job_defaults = {"coalesce": False, "max_instances": 3}


scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=get_localzone(),
)


def configure() -> None:
    """Configure APScheduler."""
    scheduler.start()
    logger.warning(f"APSScheduler configured, with SQLAlchemy job store: {scheduler}")


@elapsed_time("WARNING")
def cleanup() -> None:
    """Clean up APScheduler."""
    logger.warning(f"APScheduler is being shutdown: {scheduler}, running: {scheduler.running}")
    # Shutdown the job stores and executors but does not wait for any running tasks to complete.
    if scheduler.running:
        scheduler.shutdown(wait=False)
    logger.warning(f"APScheduler {scheduler} has been shutdown, running: {scheduler.running}")
