# WasTask Makefile
.PHONY: help install dev test format lint type-check clean docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with UV
	uv sync

dev: ## Start development server
	uv run uvicorn wastask.api.main:app --reload --host 0.0.0.0 --port 8000

cli: ## Run CLI interface
	uv run python -m wastask.cli.main

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=wastask --cov-report=html

format: ## Format code
	uv run black wastask/ tests/
	uv run ruff check wastask/ tests/ --fix

lint: ## Lint code
	uv run ruff check wastask/ tests/

type-check: ## Type check with mypy
	uv run mypy wastask/

clean: ## Clean cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache/ .mypy_cache/ .coverage dist/ build/ 2>/dev/null || true

setup-pre-commit: ## Setup pre-commit hooks
	uv run pre-commit install

update: ## Update dependencies
	uv sync --upgrade

shell: ## Open UV shell
	uv shell

info: ## Show project info
	uv tree
	@echo ""
	@echo "Project structure:"
	@find wastask -name "*.py" 2>/dev/null | head -10 || echo "No Python files found yet"

# WasTask specific commands
create-project: ## Create new project interactively
	uv run python -m wastask.cli.main project create --interactive

chat: ## Chat with WasTask AI
	uv run python -m wastask.cli.main chat "Hello WasTask!"

analyze: ## Analyze project
	uv run python -m wastask.cli.main analyze

demo: ## Run a quick demo
	@echo "🚀 WasTask Demo"
	@echo "Testing CLI..."
	uv run python -m wastask.cli.main --help
