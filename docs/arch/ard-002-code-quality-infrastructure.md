# ADR 2: Code Quality Infrastructure

## Status

Accepted

## Context

The project spans multiple test suites (SauceDemo, The Internet, UI Playground). Manual code reviews alone cannot enforce consistent formatting, type safety, and security standards across the codebase. Quality issues need to be caught before code reaches the CI/CD pipeline.

## Decision

Automated code quality is enforced via the following toolchain, integrated through [pre-commit](https://pre-commit.com/) hooks (16 hooks total, `fail_fast: false`):

**Python analysis:**

- **Ruff** — linting (13 rule categories including pycodestyle, pyflakes, isort, bugbear, pylint) and formatting, with auto-fix
- **mypy (strict mode)** — static type checking with enforced type hints on all functions (excludes `tests/`)
- **Bandit** — static security analysis for common vulnerabilities (excludes `tests/`)
- **pip-audit** — dependency vulnerability scanning against `requirements.txt`
- **Radon** — cyclomatic complexity (threshold C) and maintainability index (threshold B) checks

**File hygiene** (via `pre-commit-hooks`):

- Trailing whitespace, end-of-file fixer, YAML/TOML syntax validation
- Large file guard (500 KB), merge conflict markers, case conflict detection, LF line endings
- `no-commit-to-branch` on `main` (local safety guard; GitHub branch protection is the actual gate)

**CI enforcement:**

- GitHub Actions workflow (`code-quality.yml`) runs all pre-commit hooks on every push and PR to `main` via `pre-commit/action@v3.0.1`
- `no-commit-to-branch` is skipped in CI (`SKIP` env var) — branch protection is enforced server-side

All tool configuration is centralized in `pyproject.toml` (PEP 518). Task automation is provided via `Taskfile.yml` (`task format`, `task lint`, `task quality`, `task pre-commit`, etc.).

## Consequences

- Pre-commit hooks block commits that fail any of the 16 quality checks
- Ruff provides 10-100x faster linting compared to Flake8
- Strict mypy requires type hints on all functions — adds discipline but has a learning curve
- pip-audit catches known CVEs in dependencies before they reach `main`
- Radon flags functions with high cyclomatic complexity or low maintainability early
- Most issues are auto-fixable (Ruff, trailing whitespace, line endings), reducing developer friction
- Emergency bypass available via `--no-verify` for exceptional cases
- First-time `pre-commit install` takes ~2 minutes; subsequent runs are near-instant
