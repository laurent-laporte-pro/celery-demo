import logging
import random
import time
import typing as t
import uuid

from celery import chain, group

from celery_demo.app import celery_app
from celery_demo.progress import update_progress, init_progress

if t.TYPE_CHECKING:
    from celery.result import AsyncResult

logger = logging.getLogger(__name__)

sr = random.SystemRandom()


# ---------------------------------------------------------
# Define chain of tasks
#
# We use the following options for the tasks:
# - bind=True: the task will receive a `self` argument as the first argument.
#   It is used to introspect the task and update the progress.
# - percent: is a user-defined option to indicate the progress of the task.
#   It is used to update the progress of the job.
# ---------------------------------------------------------

@celery_app.task(bind=True, percent=20)
def task1(self, *args, job_id: str) -> None:
    """
    First task of the chain.

    Args:
        self: Current task.
        *args: Arguments transmitted to the task by the `apply_async` method.
        job_id: ID of the job.
    """
    logger.info("Processing task1 on %(job_id)s...", {"job_id": job_id})
    logger.debug(f"{args=}")
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


@celery_app.task(bind=True, percent=30)
def task2(self, *args, job_id: str) -> None:
    """
    Second task of the chain.

    Args:
        self: Current task.
        *args: Arguments transmitted by the previous task returned value, which is `(None,)`.
        job_id: ID of the job.
    """
    logger.info("Processing task2 on %(job_id)s...", {"job_id": job_id})
    logger.debug(f"{args=}")
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


@celery_app.task(bind=True, percent=50)
def subtask1(self, *args, job_id: str) -> None:
    """
    Subtask of a group, executed in parallel with `subtask2`.

    Args:
        self: Current task.
        *args: Arguments transmitted by `task2` returned value, which is `(None,)`.
        job_id: ID of the job.
    """
    logger.info("Processing subtask1...")
    logger.debug(f"{args=}")
    # The two subtasks are executed in parallel, so we cannot know, a priori, which one
    # will be executed first. We update the progress with the same value for both subtasks.
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


@celery_app.task(bind=True, percent=50)
def subtask2(self, *args, job_id: str) -> None:
    """
    Subtask of a group, executed in parallel with `subtask1`.

    Args:
        self: Current task.
        *args: Arguments transmitted by `task2` returned value, which is `(None,)`.
        job_id: ID of the job.
    """
    logger.info("Processing subtask2...")
    logger.debug(f"{args=}")
    # The two subtasks are executed in parallel, so we cannot know, a priori, which one
    # will be executed first. We update the progress with the same value for both subtasks.
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


@celery_app.task(bind=True, percent=65)
def task3(self, *args, job_id: str) -> None:
    """
    Third task of the chain (right after the group).

    Args:
        self: Current task.
        *args: Arguments transmitted by the group returned value, which is `(None, None)`,
               because the group returns the results of the two subtasks, respectively.
        job_id: ID of the job.
    """
    logger.info("Processing task3 on %(job_id)s...", {"job_id": job_id})
    logger.debug(f"{args=}")
    # the preceding tasks are a group, so this step is 3
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


@celery_app.task(bind=True, percent=85)
def task4(self, *args, job_id: str) -> None:
    """
    Last task of the chain.

    Args:
        self: Current task.
        *args: Arguments transmitted by the previous task returned value, which is `(None,)`.
        job_id: ID of the job.
    """
    logger.info("Processing task4 on %(job_id)s...", {"job_id": job_id})
    logger.debug(f"{args=}")
    update_progress(job_id, step=self.name, percent=self.percent)
    time.sleep(sr.random() * 3)


def launch_tasks() -> str:
    """
    Launches a chain of Celery tasks.

    This function creates a unique job ID and defines a chain of tasks to be executed
    sequentially. The chain includes a group of subtasks that are executed in parallel.
    The progress of the job is initialized and updated throughout the execution of the tasks.

    Returns:
        The unique job ID for the launched tasks.
    """
    job_id = f"job-{uuid.uuid4()}"
    tasks = chain(
        task1.s(job_id=job_id),
        task2.s(job_id=job_id),
        group(
            subtask1.s(job_id=job_id),
            subtask2.s(job_id=job_id),
        ),
        task3.s(job_id=job_id),
        task4.s(job_id=job_id),
    )
    result: AsyncResult = tasks.apply_async()
    init_progress(job_id, task_id=result.id)
    return job_id
