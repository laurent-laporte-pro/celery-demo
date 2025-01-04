import logging
import sys
import time
import typing as t

from celery.result import AsyncResult

from celery_demo.progress import delete_progress, get_progress
from celery_demo.tasks import launch_tasks

logger = logging.getLogger("celery_demo.demo.launch_tasks")


def print_status(job_id: str) -> str:
    progress = get_progress(job_id)
    task_id = progress["task_id"]
    result = AsyncResult(task_id)
    step = progress["step"]
    percent = progress["percent"] if result.status in {"PENDING", "STARTED"} else 100
    logger.info(
        "Job ID: %(job_id)s, Status: %(status)s, Step: %(step)s, Percent: %(percent)s",
        {"job_id": job_id, "status": result.status, "step": step, "percent": format(percent, "3d") + "%"},
    )
    return t.cast(str, result.status)


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="{levelname}: {message}", style="{")
    job_id: str = launch_tasks()
    end_time = time.time() + 15.0
    while time.time() < end_time:
        status = print_status(job_id)
        if status in {"SUCCESS", "FAILURE"}:
            break
        time.sleep(1)
    else:
        logger.error("Job did not complete in time")
    delete_progress(job_id)


if __name__ == "__main__":
    main()
