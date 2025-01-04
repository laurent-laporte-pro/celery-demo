# Celery Demo Project

This project demonstrates the use of [Celery][celery-doc] for task management and progress tracking in a Python
application.

## Project Structure

- `src/celery_demo/app.py`: Initializes the Celery application.
- `src/celery_demo/tasks.py`: Defines the Celery tasks and the task chain.
- `src/celery_demo/demo.py`: Launches the tasks and monitors their progress.
- `src/celery_demo/progress.py`: Manages the progress tracking (not provided in the context).

## Requirements

- Python 3.12+
- [Redis][redis-doc] (for Celery broker and backend)

## Installation

Required tools:

- [uv][uv-doc]: A command-line tool to manage Python virtual environments.

1. Clone the repository:
   ```sh
   git clone https://github.com/laurent-laporte-pro/celery-demo.git
   cd celery-demo
   ```

2. Create a virtual environment and install the dependencies:
   ```sh
   uv sync
   ```

3. Start Redis server:
   ```sh
   redis-server
   ```

## Usage

1. Start the Celery worker:
   ```sh
   celery -A celery-demo.app worker --loglevel=info
   # or using the demo script:
   celery-demo
   ```

2. Run the demo script:
   ```sh
   python src/celery_demo/demo.py
   ```

## Task Chain

The task chain is defined in `src/celery_demo/tasks.py` and includes the following tasks:

- `task1`: First task of the chain.
- `task2`: Second task of the chain.
- `subtask1` and `subtask2`: Subtasks executed in parallel.
- `task3`: Third task of the chain, executed after the group of subtasks.
- `task4`: Last task of the chain.

## Progress Tracking

The progress of each task is tracked and updated using the `update_progress` function.
The progress is logged and can be monitored in the console output.

## License

This project is licensed under the MIT License. See the `LICENSE.md` file for more details.


[celery-doc]: https://docs.celeryproject.org/en/stable/

[redis-doc]: https://redis.io/documentation

[uv-doc]: https://docs.astral.sh/uv/
