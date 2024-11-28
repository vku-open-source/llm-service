### Requirements

- uv for Python package and environment management.

### How to run

- uv sync
- cp .env.example .env
- Change .env environment(openai api key)
- source .venv/bin/activate
- alembic upgrade head
- fastapi dev app/main.py

## API Documents
### POST /api/v1/chat/generate-warnings
- Crawl https://nchmf.gov.vn/Kttv and process with openAI LLM
- Return processed data in json format