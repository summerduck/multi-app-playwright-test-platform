---
name: github-actions-test-pipeline
description: Generate GitHub Actions CI/CD workflows for the multi-app Playwright test platform with matrix strategy (3 apps x 3 browsers), pip/browser caching, Allure report artifacts, and pytest-xdist parallel execution. Use when creating CI pipelines, test workflows, GitHub Actions YAML, or configuring matrix test runs.
---

# GitHub Actions Test Pipeline

Generate CI/CD workflows for the multi-app Playwright test platform.

## Before Generating

1. Read `.github/workflows/code-quality.yml` — it already handles linting, formatting, type checking, and security scanning via pre-commit hooks
2. Check `pyproject.toml` for current pytest addopts, markers, and tool configuration
3. Verify `requirements.txt` for the dependency list

## Existing CI Infrastructure

### `code-quality.yml` (Already Implemented)

This workflow already runs on PR and push to `main`:
- Uses `pre-commit/action@v3.0.1` to run all 16 pre-commit hooks
- Covers: Ruff lint + format, mypy strict, Bandit security, radon complexity, pip-audit
- Uses `actions/checkout@v4`, `actions/setup-python@v5` with Python 3.12
- Concurrency with `cancel-in-progress: true`
- Skips `no-commit-to-branch` in CI (branch protection handles this)

**Do not duplicate quality checks in the test workflow.** The test workflow depends on `code-quality.yml` passing (or runs independently — both approaches work since quality checks are fast).

## Project Context

- **Python:** 3.12
- **Browsers:** Chromium, Firefox, WebKit (via Playwright 1.51.0)
- **App markers:** `saucedemo`, `theinternet`, `uiplayground` (defined in `pyproject.toml`)
- **Parallelism:** pytest-xdist (`-n auto`)
- **Automatic addopts** (from `pyproject.toml`): `--reruns=1`, `--alluredir=allure-report`, `--cov=pages --cov=utils --cov=config`, `--html=report.html`, `-v --tb=short --strict-markers`
- **Environment:** `USER_PASSWORD` env var (used by `conftest.py` via `--user-pw` or `USER_PASSWORD`)
- **Artifacts from conftest.py:**
  - `test-logs/screenshots/` — failure screenshots (attached to Allure)
  - `test-logs/traces/` — Playwright traces (attached to Allure)
  - `test-logs/failed_tests/` — per-test log files for failed tests
- **Action versions** (match `code-quality.yml`): `checkout@v4`, `setup-python@v5`, `cache@v4`, `upload-artifact@v4`

## Caching Strategy

| Cache target | Key strategy | Path | When invalidated |
|-------------|-------------|------|-----------------|
| pip packages | `hashFiles('requirements.txt')` | `~/.cache/pip` | Dependency update |
| Playwright browsers | browser name + `hashFiles('requirements.txt')` | `~/.cache/ms-playwright` | Playwright version bump in `requirements.txt` |

Note: `code-quality.yml` uses `setup-python` built-in `cache: "pip"` instead of manual `actions/cache`. Both approaches work — the test workflow uses explicit caching for Playwright browser caching alongside pip.

## Required GitHub Repository Configuration

Before the test workflow runs:
1. Add `USER_PASSWORD` to repository Settings → Secrets → Actions secrets
2. The `.env` file is not committed (listed in `.gitignore`); CI uses secrets instead

## Rules

- `fail-fast: false` in matrix — failing one app/browser must not cancel others
- `concurrency` with `cancel-in-progress: true` — matches `code-quality.yml` pattern
- Upload Allure results with `if: always()` — reports needed for failed runs
- Upload screenshots/traces only on `if: failure()` to save storage
- `--with-deps` when installing Playwright browsers (installs OS-level libraries)
- Pin action versions to major tags (`@v4`, `@v5`) — matches `code-quality.yml`
- Do not duplicate quality checks (lint, format, type check, security) — `code-quality.yml` handles this
- Do not repeat `pyproject.toml` addopts in the pytest command — they apply automatically
- `workflow_dispatch` trigger on main test workflow for manual runs
