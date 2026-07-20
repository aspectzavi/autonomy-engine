.PHONY: install format lint test run clean

install:
	pip install -r requirements.txt
	playwright install chromium

format:
	black backend
	isort backend

lint:
	ruff check backend
	mypy backend

test:
	pytest

run:
	uvicorn backend.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete