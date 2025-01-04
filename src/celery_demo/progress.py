"""
This module manages the recording of the main job states. Each job is associated with a main task
which is composed of a chain of subtasks. The purpose of this module is to track the processing progression.
"""

import typing as t

from redis import Redis

redis_client: Redis = Redis(host="localhost", port=6379, db=0)


class Progress(t.TypedDict):
    """
    A dictionary containing the task ID, current step, and completion percentage of the job.
    """

    task_id: str
    step: str
    percent: int


def init_progress(job_id: str, *, task_id: str) -> None:
    """
    Initialize the progress tracking for a job.

    This function is called right after the main task is created.

    Args:
        job_id: The unique identifier for the job.
        task_id: The unique identifier for the main task of the job.
    """
    progress_key: str = f"workflow:{job_id}:progress"
    redis_client.hset(progress_key, "task_id", task_id)
    redis_client.hset(progress_key, "step", "<start>")
    redis_client.hset(progress_key, "percent", "0")


def update_progress(job_id: str, *, step: str, percent: int) -> None:
    """
    Update the progress of a job.

    This function is called asynchronously by the tasks to update the job's progress.

    Args:
        job_id: The unique identifier for the job.
        step: The current step of the job.
        percent: The completion percentage of the job.
    """
    progress_key: str = f"workflow:{job_id}:progress"
    redis_client.hset(progress_key, "step", step)
    redis_client.hset(progress_key, "percent", str(percent))


def get_progress(job_id: str) -> Progress:
    """
    Retrieve the progress of a job.

    This function is called by the monitoring process to get the current status of the job.

    Args:
        job_id: The unique identifier for the job.

    Returns:
        A dictionary containing the task ID, current step, and completion percentage of the job.
    """
    progress_key: str = f"workflow:{job_id}:progress"
    values: dict[bytes, bytes] = redis_client.hgetall(progress_key)
    decoded_values: dict[str, str] = {k.decode(): v.decode() for k, v in values.items()}
    return {
        "task_id": decoded_values.get("task_id", "<unknown>"),
        "step": decoded_values.get("step", "<idle>"),
        "percent": int(decoded_values.get("percent", 0)),
    }


def delete_progress(job_id: str) -> None:
    """
    Delete the progress tracking for a job.

    This function is called after the job is completed or terminated to clean up the progress tracking.

    Args:
        job_id: The unique identifier for the job.
    """
    progress_key: str = f"workflow:{job_id}:progress"
    redis_client.delete(progress_key)
