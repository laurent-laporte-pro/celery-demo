"""
Celery app
"""

from celery import Celery

celery_app = Celery(
    "celery_demo",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["celery_demo.tasks"],
)

celery_app.conf.broker_connection_retry_on_startup = True
