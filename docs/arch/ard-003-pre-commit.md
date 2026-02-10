# ADR 0: Migrate from Custom Git Hooks to pre-commit Framework

## Status

Accepted

## Context

The project uses a hand-written bash script (`.githooks/pre-commit`) as a Git hook. This script manually manages venv activation, staged file lists, and exit codes. It has limited coverage (only `.py` and `.json` files for secrets), a known bypass bug in the secrets scanner, and is difficult to maintain.

## Decision

Replace the custom shell-based Git hook with the [pre-commit](https://pre-commit.com/) framework, configured via `.pre-commit-config.yaml`.

Key changes:

- Declarative YAML config with versioned, auto-managed hooks
- Ruff instead of Black for formatting
- Bandit instead of regex patterns for security scanning
- Broader file coverage (YAML, TOML, line endings, case conflicts, large files, type checking)

## Consequences

- No manual bash logic to maintain
- Hooks are reproducible across environments
- Broader and more reliable code quality checks
- Team members need `pre-commit install` in their local setup
