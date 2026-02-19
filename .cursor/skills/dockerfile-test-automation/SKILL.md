---
name: dockerfile-test-automation
description: Generate Dockerfiles and Docker Compose configurations for the multi-app Playwright test platform with multi-stage builds, layer caching, non-root user security, and single-browser CI builds. Use when creating Dockerfiles, Docker Compose files, containerizing tests, or setting up Docker-based test infrastructure.
---

# Dockerfile Test Automation

Generate Docker configurations for the multi-app Playwright test platform.

## Before Generating

1. Read `requirements.txt` for the current dependency list (pinned versions)
2. Check `pyproject.toml` for Python version (`>=3.12`) and pytest addopts
3. Check `Taskfile.yml` for existing task definitions that Docker commands should align with

## Project Context

- **Python:** 3.12 (`requires-python = ">=3.12"` in `pyproject.toml`)
- **Playwright:** 1.51.0 (pinned in `requirements.txt`)
- **Dependencies:** `requirements.txt` with pinned versions
- **Test runner:** `pytest` with addopts from `pyproject.toml` (includes `--reruns=1`, `--alluredir=allure-report`, `--cov`)
- **Parallelism:** pytest-xdist (`-n auto`)
- **Test artifacts:**
  - `test-logs/` — per-test logs, `test-logs/screenshots/`, `test-logs/traces/`, `test-logs/failed_tests/`
  - `allure-report/` — Allure results
  - `htmlcov/` — coverage HTML report
  - `report.html` — pytest-html report
- **Environment:** `USER_PASSWORD` env var (loaded via `python-dotenv` in `conftest.py`)
- **Task runner:** `Taskfile.yml` (use `task test`, `task test-parallel`, etc.)

## Multi-Stage Dockerfile

```dockerfile
# ── Stage 1: Dependencies ─────────────────────────────────────────────────
FROM python:3.12-slim AS dependencies

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Browsers ────────────────────────────────────────────────────
FROM dependencies AS browsers

RUN playwright install --with-deps chromium firefox webkit

# ── Stage 3: Runtime ─────────────────────────────────────────────────────
FROM browsers AS runtime

RUN groupadd --gid 1000 testuser \
    && useradd --uid 1000 --gid testuser --shell /bin/bash --create-home testuser

WORKDIR /app

# Copy application code (order: least → most frequently changed)
COPY pyproject.toml conftest.py ./
COPY config/ config/
COPY utils/ utils/
COPY pages/ pages/
COPY tests/ tests/

# Create artifact directories matching conftest.py log_helpers.py layout
RUN mkdir -p test-logs/failed_tests test-logs/screenshots test-logs/traces \
             allure-report htmlcov \
    && chown -R testuser:testuser /app

USER testuser

# pytest addopts in pyproject.toml handle most flags automatically
ENTRYPOINT ["pytest"]
CMD ["tests/", "-n", "auto"]
```

## Single-Browser Dockerfile (for CI Matrix Jobs)

Each CI matrix job tests one browser. This image is ~400MB smaller than the all-browsers image:

```dockerfile
FROM python:3.12-slim AS base

ARG BROWSER=chromium

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps ${BROWSER}

RUN groupadd --gid 1000 testuser \
    && useradd --uid 1000 --gid testuser --shell /bin/bash --create-home testuser

COPY pyproject.toml conftest.py ./
COPY config/ config/
COPY utils/ utils/
COPY pages/ pages/
COPY tests/ tests/

RUN mkdir -p test-logs/failed_tests test-logs/screenshots test-logs/traces \
             allure-report htmlcov \
    && chown -R testuser:testuser /app

USER testuser

ENTRYPOINT ["pytest"]
CMD ["tests/", "-n", "auto"]
```

Build per browser: `docker build --build-arg BROWSER=firefox -t tests-firefox .`

## Docker Compose

```yaml
services:
  # ── Test Runner ───────────────────────────────────────────────────────
  tests:
    build:
      context: .
      dockerfile: Dockerfile
      target: runtime
    environment:
      - USER_PASSWORD=${USER_PASSWORD}
    volumes:
      - ./test-logs:/app/test-logs
      - ./allure-report:/app/allure-report
      - ./htmlcov:/app/htmlcov
      - ./report.html:/app/report.html
    # pytest addopts in pyproject.toml handle --alluredir, --cov, --reruns, etc.
    command: ["tests/", "-n", "auto"]

  # ── Allure Report Server ──────────────────────────────────────────────
  allure:
    image: frankescobar/allure-docker-service:latest
    ports:
      - "5050:5050"
    environment:
      CHECK_RESULTS_EVERY_SECONDS: 5
      KEEP_HISTORY: "1"
    volumes:
      - ./allure-report:/app/allure-results
      - allure-reports:/app/default-reports

volumes:
  allure-reports:
```

Usage:
- Run all tests: `docker compose run --rm tests`
- Run single app: `docker compose run --rm tests tests/ -m saucedemo`
- Run single app + browser: `docker compose run --rm tests tests/ -m saucedemo --browser chromium`
- Smoke tests only: `docker compose run --rm tests tests/ -m smoke`
- Start Allure server: `docker compose up allure`
- View Allure: `http://localhost:5050`

## .dockerignore

Excludes all non-essential files from the build context:

```
# Version control & CI
.git
.github
.pre-commit-config.yaml

# IDE and project metadata
.cursor
.notes
.editorconfig
docs/

# Python caches
.mypy_cache
.pytest_cache
.ruff_cache
__pycache__
*.pyc
*.pyo

# Virtual environment
venv/
.venv/

# Secrets
.env

# Test artifacts (generated at runtime, mounted as volumes)
test-logs/
allure-report/
allure-results/
htmlcov/
report.html

# Other
node_modules/
*.egg-info
.tox
Taskfile.yml
README.md
LICENSE
```

## Layer Caching Strategy

Layers ordered from least to most frequently changed:

1. **Base image** (`python:3.12-slim`) — rarely changes
2. **pip install** from `requirements.txt` — changes when dependencies update
3. **Playwright browser install** — changes when Playwright version bumps
4. **`pyproject.toml` + `conftest.py`** — changes less often than test code
5. **`utils/` + `pages/`** — framework code, moderate change frequency
6. **`tests/`** — changes on every feature branch

`requirements.txt` is copied and installed before application code so pip install layer is cached when only code changes.

## Rules

- Multi-stage builds: separate dependency install from runtime
- Non-root user (`testuser` UID 1000): switch before `ENTRYPOINT`
- Artifact directories must match `conftest.py` layout: `test-logs/failed_tests/`, `test-logs/screenshots/`, `test-logs/traces/`
- `USER_PASSWORD` passed via environment variable, never in Dockerfile
- `--no-cache-dir` on every `pip install`
- `--with-deps` on every `playwright install` (installs OS-level libraries)
- `BROWSER` build arg for CI matrix: `--build-arg BROWSER=chromium`
- Mount artifact directories as volumes in Docker Compose
- `pyproject.toml` addopts handle `--alluredir`, `--cov`, `--reruns` — do not duplicate in `CMD`
