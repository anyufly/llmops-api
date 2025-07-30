# llmops-api
https://docs.astral.sh/uv/#highlights
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run alembic -x load_from_env -x pg_schema=llmops_api upgrade head
uv run alembic -x load_from_env -x pg_schema=llmops_api revision --autogenerate -m "comment"
uv run uvicorn llmops_api.main:app --host 0.0.0.0 --port 8080 --workers 8
uv run celery -A llmops_api.celery.base.app worker -l INFO -c 4