.PHONY: runserver coverage migrations test lint format admin reset-db install

install:
	pip install -r requirements-dev.txt

runserver:
	docker compose up database -d
	sleep 2
	uvicorn app.main:app --reload --host=localhost --port=8000

test:
	PYTHONPATH=. pytest -v --disable-warnings

coverage:
	PYTHONPATH=. pytest --cov=app --cov-report=xml --cov-report=term --cov-fail-under=80 --disable-warnings

lint:
	ruff check app tests
	mypy app --ignore-missing-imports

format:
	ruff format app tests
	ruff check --fix app tests

migrations:
	alembic revision --autogenerate -m "$(message)"
	@echo "Migrations created successfully"

migrate:
	alembic upgrade head
	@echo "Migrations applied successfully"

admin:
	PYTHONPATH=. python scripts/create_admin.py

reset-db:
	docker compose down -v
	docker compose up database -d
	@sleep 3
	PYTHONPATH=. alembic upgrade head
	@echo "Database reset complete"
