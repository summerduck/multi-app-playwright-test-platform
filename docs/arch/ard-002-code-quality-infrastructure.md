# ADR 2: Code Quality Infrastructure

## Status

Accepted

## Context

The project spans multiple test suites (SauceDemo, The Internet, UI Playground). Manual code reviews alone cannot enforce consistent formatting, type safety, and security standards across the codebase. Quality issues need to be caught before code reaches the CI/CD pipeline.

## Decision

We will enforce automated code quality via the following toolchain, integrated through pre-commit hooks:

- **Ruff** — fast linting (Rust-based, replaces Flake8 + plugins), with auto-fix
- **mypy (strict mode)** — static type checking with 100% type hint coverage
- **Bandit** — static security analysis for common vulnerabilities

All tool configuration is centralized in `pyproject.toml` (PEP 518). Task automation is provided via `Taskfile.yml` (`task format`, `task lint`, `task quality`, etc.).

## Consequences

- Pre-commit hooks block commits that fail any of the 14 quality checks
- Ruff provides 10-100x faster linting compared to Flake8
- Strict mypy requires type hints on all functions — adds discipline but has a learning curve
- Most issues are auto-fixable (Ruff), reducing developer friction
- Emergency bypass available via `--no-verify` for exceptional cases
- First-time `pre-commit install` takes ~2 minutes; subsequent runs are near-instant
