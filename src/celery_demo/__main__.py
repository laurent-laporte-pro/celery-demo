"""
Application entry point: run the celery worker.
"""

from celery_demo.app import celery_app


def main():
    celery_app.start(["worker", "--loglevel=INFO"])


if __name__ == "__main__":
    main()
