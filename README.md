# 🎭 Multi-App Playwright Test Platform

[![Code Quality](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.51+-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![Ruff](https://img.shields.io/badge/linting-Ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A test automation framework for E2E testing across multiple web applications, built with Playwright and Python.

---

## Applications Under Test

| Application | URL | Focus Area |
|-------------|-----|------------|
| **SauceDemo** | [saucedemo.com](https://www.saucedemo.com/) | E-commerce flows |
| **The Internet** | [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) | Complex UI patterns |
| **UI Testing Playground** | [uitestingplayground.com](http://uitestingplayground.com/) | Dynamic elements & timing |

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **E2E Testing** | Playwright, pytest, pytest-xdist, pytest-playwright |
| **Code Quality** | Ruff, mypy (strict), Bandit, pip-audit, Radon |
| **CI/CD** | GitHub Actions (code quality + test workflows) |
| **Reporting** | Allure, pytest-html |
| **Task Runner** | [Task](https://taskfile.dev/) (`Taskfile.yml`) |
| **Configuration** | `pyproject.toml` (PEP 518, centralized) |

---

## Quick Start

### Prerequisites

- Python 3.10+
- [Task](https://taskfile.dev/) (optional, for task runner commands)

### Setup

```bash
# Clone and enter the project
git clone https://github.com/your-username/multi-app-playwright-test-platform
cd multi-app-playwright-test-platform

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies + Playwright browsers
task install
# or without Task:
pip install -r requirements.txt && playwright install chromium

# Install pre-commit hooks
task pre-commit-install
# or: pre-commit install
```

### Running Tests

```bash
task test                    # Run all tests
task test-parallel           # Run tests in parallel
task test-headed             # Run in headed mode (visible browser)

# Or directly with pytest:
pytest tests/saucedemo/      # Run SauceDemo tests
pytest tests/ -n auto        # Run all tests in parallel
pytest -m smoke              # Run smoke tests only
```

### Code Quality

```bash
task pre-commit              # Run all 16 pre-commit hooks
task quality                 # Run format + lint + type-check + security
task format                  # Format code with Ruff
task lint                    # Lint with Ruff
task type-check              # Type check with mypy
task security                # Security scan with Bandit
```

---

## Code Quality Infrastructure

Quality is enforced automatically via **16 pre-commit hooks** that run locally on every commit and in CI on every PR. See [ADR-002](docs/arch/ard-002-code-quality-infrastructure.md) for full rationale.

**Python analysis:**

- **Ruff** — linting (13 rule categories) and formatting, with auto-fix
- **mypy (strict)** — static type checking with enforced type hints (excludes `tests/`)
- **Bandit** — security analysis for common vulnerabilities (excludes `tests/`)
- **pip-audit** — dependency vulnerability scanning
- **Radon** — cyclomatic complexity (threshold C) and maintainability index (threshold B)

**File hygiene:**

- Trailing whitespace, EOF fixer, YAML/TOML validation, large file guard (500 KB), merge conflict markers, case conflicts, LF line endings

**CI enforcement:**

- `code-quality.yml` — runs all pre-commit hooks via `pre-commit/action@v3.0.1`
- `tests.yml` — runs pytest with Playwright, uploads test artifacts

---

## Project Structure

```
├── pages/                   # Page Objects (per application)
│   ├── base_page.py
│   ├── saucedemo/
│   ├── the_internet/
│   └── ui_playground/
├── tests/                   # Test suites (per application)
│   ├── saucedemo/
│   ├── the_internet/
│   ├── ui_playground/
│   └── framework/           # Framework unit tests
├── utils/                   # Shared utilities
├── config/                  # Configuration modules
├── performance/             # Performance testing (Locust)
├── scripts/                 # Helper scripts
├── docs/arch/               # Architecture Decision Records
├── .github/workflows/       # CI pipelines
├── conftest.py              # Root pytest configuration
├── pyproject.toml           # Centralized tool configuration
├── Taskfile.yml             # Task runner commands
├── .pre-commit-config.yaml  # Pre-commit hooks
└── requirements.txt         # Pinned dependencies
```

---

## Architecture Decisions

| ADR | Decision |
|-----|----------|
| [ADR-001](docs/arch/ard-001-playwright-selection.md) | Playwright as the E2E testing framework |
| [ADR-002](docs/arch/ard-002-code-quality-infrastructure.md) | Code quality infrastructure and toolchain |
| [ADR-003](docs/arch/ard-003-pre-commit.md) | Migration from custom git hooks to pre-commit |
| [ADR-004](docs/arch/ard-004-git-strategy.md) | Git branching strategy (GitHub Flow) |

---

## Project Status

### Tier 1: Core (In Progress)

**Foundation & Setup**
- [x] Project structure and scaffolding
- [x] Code quality infrastructure (16 pre-commit hooks)
- [x] CI/CD pipelines (code quality + tests)
- [x] Centralized configuration (`pyproject.toml`)
- [x] Task runner (`Taskfile.yml`)
- [x] Architecture Decision Records
- [x] PR template and branching strategy

**Test Suites**
- [ ] SauceDemo — BasePage, Page Objects, 20 E2E tests
- [ ] The Internet — Dynamic Loading, File Upload, Auth, Frames, 10 tests
- [ ] UI Playground — Dynamic ID, Class Attribute, Hidden Layers, 10 tests

**Infrastructure**
- [ ] Docker containerization (multi-stage, <800MB)
- [ ] GitHub Actions matrix strategy (3 apps x 3 browsers)
- [ ] Performance testing (Locust)
- [ ] Kubernetes deployment (Jobs, ConfigMaps, CronJobs)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Allure reporting with history trends

### Tier 2 (Planned)

- [ ] Visual regression testing (Playwright screenshots)
- [ ] Accessibility testing (axe-core, WCAG 2.1 AA)
- [ ] Flaky test detection and smart test selection
- [ ] Infrastructure as Code (Terraform — AWS ECR, S3, CloudWatch)
- [ ] Structured logging (structlog) and log aggregation
- [ ] Runbooks and CONTRIBUTING.md

### Tier 3 (Future)

- [ ] AWS cloud deployment (EKS/ECS, VPC, IAM)
- [ ] Distributed tracing (Jaeger/Tempo)
- [ ] Contract testing (Pact)
- [ ] Security testing (OWASP ZAP)

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
