.PHONY: help install install-dev test test-cov test-fast lint format security clean run

# Default target
help:
	@echo "SPMv1.0 - Development Commands"
	@echo "=============================="
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run all tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make test-fast    - Run tests in parallel (faster)"
	@echo "  make test-watch   - Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linters (flake8, ruff)"
	@echo "  make format       - Format code (black, isort)"
	@echo "  make security     - Run security checks (bandit, safety)"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run development server"
	@echo "  make clean        - Clean generated files"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
	@echo ""
	@echo "✅ Coverage report generated in htmlcov/index.html"

test-fast:
	pytest tests/ -n auto --dist loadfile

test-watch:
	pytest-watch tests/

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo ""
	@echo "Running ruff..."
	ruff check src/ tests/
	@echo ""
	@echo "✅ Linting complete"

format:
	@echo "Formatting with black..."
	black src/ tests/
	@echo ""
	@echo "Sorting imports with isort..."
	isort src/ tests/
	@echo ""
	@echo "✅ Formatting complete"

# Security
security:
	@echo "Running bandit..."
	bandit -r src/ -ll
	@echo ""
	@echo "Running safety..."
	safety check
	@echo ""
	@echo "Running pip-audit..."
	pip-audit
	@echo ""
	@echo "✅ Security checks complete"

# Development
run:
	python src/backend/app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"
