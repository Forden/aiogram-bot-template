PROJECT_DIR=aiogram_bot_template

all: lint

lint:
	poetry run python -m ruff $(PROJECT_DIR) --config pyproject.toml --fix
	poetry run python -m isort $(PROJECT_DIR)
	poetry run python -m mypy $(PROJECT_DIR) --config-file pyproject.toml
	poetry run python -m black $(PROJECT_DIR) --config pyproject.toml