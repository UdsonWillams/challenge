.PHONY: runserver coverage migrations

runserver:
	docker compose up database -d
	uvicorn app.main:app --reload --host=localhost --port=8080

coverage:
	PYTHONPATH=. pytest --cov=app --cov-report=xml --cov-fail-under=55 --disable-warnings

migrations:
	alembic revision --autogenerate -m $(message)
	@echo "Migrations created successfully"
	@echo "Don't forget to edit the new migration file if necessary"
