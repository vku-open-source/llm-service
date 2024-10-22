### Requirements
- Docker.
- uv for Python package and environment management.

### How to run
- docker compose -f docker-compose-dev.yml watch
- uv sync
- source .venv/bin/activate
- fastapi dev app/main.py