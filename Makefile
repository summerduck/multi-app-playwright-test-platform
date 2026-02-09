.PHONY: help install install-dev install-browsers test test-parallel test-verbose test-headed test-specific test-markers format lint type-check pre-commit clean clean-all report allure-report allure-serve

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip
PYTEST := pytest
BROWSER := chromium

# Colors for help
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

## help: Show this help message
help:
	@echo "$(BLUE)Available make targets:$(NC)"
	@echo ""
	@echo "$(GREEN)Installation:$(NC)"
	@echo "  make install          - Install everything (deps + browsers)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make format           - Format code with black and isort"
	@echo "  make lint             - Run linting (pylint + flake8)"
	@echo "  make quality          - Run all quality checks (format + lint + type-check)"
	@echo ""
	@echo "$(GREEN)Pre-commit:$(NC)"
	@echo "  make pre-commit       - Run pre-commit hooks on all files"
	@echo "  make pre-commit-install - Install pre-commit hooks"
	@echo "  make pre-commit-update - Update pre-commit hooks"
	@echo ""
	@echo "$(GREEN)Reports:$(NC)"
	@echo "  make report           - Open HTML test report"
	@echo "  make allure-report    - Generate Allure report"
	@echo "  make allure-serve     - Generate and serve Allure report"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean            - Clean test artifacts and cache"
	@echo "  make clean-all        - Deep clean (including venv and all reports)"
	@echo ""

## Installation targets

## install: Install production dependencies
install:
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"
	@echo "$(BLUE)Installing Playwright browsers...$(NC)"
	playwright install $(BROWSER)
	@echo "$(GREEN)Playwright browsers installed successfully!$(NC)"

## Testing targets

## Code quality targets

## format: Format code with black and isort
format:
	@echo "$(BLUE)Formatting code with black...$(NC)"
	black .
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	isort .
	@echo "$(GREEN)Code formatting complete!$(NC)"

## lint: Run linting tools
lint:
	@echo "$(BLUE)Running pylint...$(NC)"
	pylint pages/ tests/ utils/ || true
	@echo "$(BLUE)Running flake8...$(NC)"
	flake8 pages/ tests/ utils/ || true
	@echo "$(GREEN)Linting complete!$(NC)"

## quality: Run all quality checks
quality: format lint type-check
	@echo "$(GREEN)All quality checks complete!$(NC)"


## Report targets

## report: Open HTML test report
report:
	@if [ -f report.html ]; then \
		echo "$(BLUE)Opening HTML test report...$(NC)"; \
		open report.html || xdg-open report.html 2>/dev/null || echo "$(YELLOW)Please open report.html manually$(NC)"; \
	else \
		echo "$(YELLOW)No report.html found. Run tests first.$(NC)"; \
	fi

## allure-report: Generate Allure report
allure-report:
	@echo "$(BLUE)Generating Allure report...$(NC)"
	allure generate allure-report -o allure-results --clean
	@echo "$(GREEN)Allure report generated in allure-results/$(NC)"

## allure-serve: Generate and serve Allure report
allure-serve:
	@echo "$(BLUE)Generating and serving Allure report...$(NC)"
	allure serve allure-report

## Cleanup targets

## clean: Clean test artifacts and cache
clean:
	@echo "$(BLUE)Cleaning test artifacts and cache...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf .mypy_cache .tox .coverage htmlcov 2>/dev/null || true
	rm -rf test-results/ test-logs/ 2>/dev/null || true
	rm -f report.html result.xml 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(NC)"

## clean-all: Deep clean including venv and reports
clean-all: clean
	@echo "$(BLUE)Performing deep clean...$(NC)"
	rm -rf venv/ 2>/dev/null || true
	rm -rf allure-report/ allure-results/ 2>/dev/null || true
	rm -rf logs/ 2>/dev/null || true
	@echo "$(GREEN)Deep cleanup complete!$(NC)"
