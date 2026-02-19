# ADR 4: AI Skills for Codified Project Standards

## Status

Accepted

## Context

The project requires consistent code generation across multiple contributors (human and AI) for page objects, tests, workflows, Dockerfiles, CI workflows, performance tests, and documentation. Without codified standards, each generation produces inconsistent patterns — different locator strategies, missing Allure annotations, inconsistent logging, or non-standard file placement.

The framework has established conventions (BasePage inheritance, per-app `base_url` fixtures, per-test FileHandler logging, Allure step decorators, method chaining with `Self`, 17 pytest markers, xdist-aware artifact management) that must be followed in every new file. Manual enforcement through code review is slow and error-prone.

Alternatives considered: project wiki with copy-paste templates, custom CLI scaffolding tool (cookiecutter/copier), relying solely on linting rules and pre-commit hooks.

## Decision

The project uses [AI Skills](https://docs.cursor.com) — structured markdown files in `.cursor/skills/` — to encode project-specific conventions, templates, and generation rules for AI-assisted development.

Each skill references the actual project files (`conftest.py`, `pyproject.toml`, `Taskfile.yml`, `utils/log_helpers.py`, `.github/workflows/code-quality.yml`) rather than documenting generic best practices. Skills encode what makes this project different, not what can be found in official documentation.

Skills created (9 total):

- **playwright-page-object-generator** — BasePage inheritance, Locator objects in `__init__`, Allure steps, method chaining; examples use actual SauceDemo/The Internet/UI Playground pages; documents per-app `base_url` fixture convention
- **pytest-test-scaffolder** — AAA pattern, all 17 pytest markers, conftest fixture documentation including per-app `base_url` fixtures, `pyproject.toml` addopts awareness (`--reruns=1`, `--strict-markers`, `--cov`)
- **allure-report-enhancer** — report hierarchy mapped to the 3-app structure (epic per app), severity mapping per app, decorator order convention, references existing `conftest.py` failure artifact hooks
- **adr-writer** — Cognitect ADR format matching existing `docs/arch/` convention with `ard-` prefix, references existing ADRs and planned ADRs from roadmap
- **dockerfile-test-automation** — multi-stage builds, artifact directories matching `conftest.py` log layout, `.dockerignore` covering project-specific directories (`.notes/`, `.cursor/`, `docs/`)
- **github-actions-test-pipeline** — matrix strategy (3 apps × 3 browsers), documents relationship to existing `code-quality.yml` (no duplication of quality checks), `pyproject.toml` addopts apply automatically
- **workflow-pattern-generator** — orchestrates multiple page objects into reusable e2e business flows; Workflow Layer sits between test and POM layers; Allure step decorators on every public method, `Self` return for chaining, `config.data.models` dataclasses for parameters; cross-references playwright-page-object-generator, pytest-test-scaffolder, and allure-report-enhancer skills
- **locust-performance-test** — app-specific HTTP scenarios (SauceDemo checkout flow, The Internet page loads), conservative user counts for third-party public apps, Taskfile integration
- **code-quality-standards** — single source of truth for all Python code quality requirements derived from `pyproject.toml`: import order (isort groups), type annotation rules (mypy strict, Python 3.12 syntax), ruff rule reference (`B006`, `PTH`, `ERA`, `RET`, `ARG`, `SIM`), bandit constraints, and per-file exemptions (`tests/*`, `conftest.py`); all other skills reference this skill instead of duplicating quality rules

After initial creation, the skills were audited for cross-skill contradictions. Issues resolved included: POM methods returning other page object types instead of `Self` (visible in examples across three skills), `verify_*` methods lacking a specified assertion mechanism (`expect()` vs `assert`), inconsistent `assert` prohibition in tests, scenario file naming for Locust (`theinternet` vs `the_internet`), and a mutable default argument in a workflow example.

Reasons:

- Skills are version-controlled alongside the codebase — changes are reviewed in PRs
- Each skill encodes the project's specific conventions, not generic best practices — locator priority lists and Docker security basics belong in official docs, not skills
- Skills reference existing project files (`conftest.py` hooks, per-app `base_url` fixtures, `pyproject.toml` markers, `code-quality.yml`) for accurate context
- code-quality-standards centralises linting rules so that each skill stays focused on its domain; updating `pyproject.toml` requires changing one skill, not eight
- AI generates code that passes existing quality gates (Ruff, mypy strict, Bandit) on first attempt — import order, modern Python 3.12 syntax, mutable default guards, and per-file exemptions are explicit in the skill
- New patterns only need to be defined once — every subsequent generation follows them
- Skills cross-reference each other — the test scaffolder references the page object and Allure skills, the CI skill references the existing code-quality workflow
- Cross-skill consistency is enforceable: a single audit pass identified and resolved six contradictions across three skills, demonstrating that skills are maintainable documentation, not write-once artefacts

## Consequences

- Every new page object, test file, workflow, Dockerfile, and CI workflow follows established project conventions without manual review of style guides
- Skills must be updated when project conventions change (e.g., new `conftest.py` fixtures, new pytest markers in `pyproject.toml`, new app `base_url` fixtures) — stale skills produce incorrect code; code-quality-standards must be updated when `pyproject.toml` linting configuration changes
- Skills are Cursor-specific — contributors using other editors do not benefit from automated generation but can reference the markdown files as living documentation
- The `.cursor/skills/` directory adds files to the repository that are not runtime code
- Skills reduce onboarding time — a new contributor generates correctly structured files immediately
- Removing generic content from skills means contributors must consult official Playwright/Docker/Locust documentation for fundamentals — skills assume familiarity with the tools
- Skills require periodic consistency audits — contradictions between skills accumulate as conventions evolve and must be resolved before they cause divergent generated code
