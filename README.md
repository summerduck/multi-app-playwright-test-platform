# Multi-App Playwright Test Platform

[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue?logo=python&logoColor=white)](https://www.python.org)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A unified test automation framework for E2E and performance testing across multiple web applications. Built with Playwright, Python, and cloud-native infrastructure.

**Current Focus:** Tier 1 implementation (core testing platform with Docker, Kubernetes, CI/CD, and monitoring)

---

## Overview

This framework provides a production-ready test automation platform with a tier-based implementation approach:

### Tier 1 Features (Current Scope)
- **Multi-App Architecture** — Unified testing framework for multiple applications
- **Cloud-Native Infrastructure** — Docker and Kubernetes deployment
- **CI/CD Integration** — GitHub Actions with matrix strategy, parallel execution
- **Observability** — Prometheus metrics, Grafana dashboards, Allure reports
- **Performance Testing** — Integrated Locust load testing
- **Code Quality** — Type safety, linting, security scanning, pre-commit hooks

### Future Enhancements (Tier 2 & 3)
- Visual regression testing
- Accessibility testing (WCAG 2.1)
- AWS cloud deployment (EKS, ECR, S3)
- Terraform infrastructure as code
- Advanced monitoring and smart test selection

---

## Applications Under Test

| Application | URL | Focus Area | Complexity |
|-------------|-----|------------|------------|
| **SauceDemo** | [saucedemo.com](https://www.saucedemo.com/) | E-commerce flows | Intermediate |
| **The Internet** | [the-internet.herokuapp.com](https://the-internet.herokuapp.com/) | Complex UI patterns | Intermediate-Advanced |
| **UI Testing Playground** | [uitestingplayground.com](http://uitestingplayground.com/) | Dynamic elements & timing | Advanced |

---

## Features

### Testing Framework
- **Playwright + Python** — Modern async E2E testing with multi-browser support
- **Page Object Model** — Maintainable, reusable page abstractions
- **pytest** — Industry-standard test framework with rich plugin ecosystem
- **Type Safety** — 100% type hints coverage with mypy strict mode

### Multi-App Strategy
- **Unified Framework** — Shared base classes, utilities, and configuration
- **Independent Test Suites** — Isolated test execution per application
- **Parallel Execution** — pytest-xdist for concurrent test runs
- **Cross-Browser Testing** — Chromium, Firefox, WebKit support

### Infrastructure
- **Docker** — Multi-stage builds optimized for size (<800MB)
- **Kubernetes** — Manifests with resource limits, health probes, CronJobs
- **CI/CD** — GitHub Actions with matrix strategy (3 apps × 3 browsers)
- **AWS** — TBD (Tier 2: EKS, ECR, S3 deployment)

### Observability
- **Prometheus** — Custom metrics for test execution, duration, success rates
- **Grafana** — Real-time dashboards for test and performance metrics
- **Allure Reports** — Rich HTML reports with screenshots, videos, traces
- **Structured Logging** — JSON logs for easy parsing and analysis

### Testing Types
- **E2E Tests** — Comprehensive user journey testing
- **Performance** — Locust load testing scenarios
- **Security** — Trivy container scanning
- **Visual Regression** — TBD (Tier 2: Playwright screenshot comparison)
- **Accessibility** — TBD (Tier 2: axe-core WCAG 2.1 AA compliance)

### Code Quality
- **Pre-commit Hooks** — Automated formatting and linting
- **Black** — Consistent code formatting
- **mypy** — Static type checking (strict mode)
- **Ruff/Flake8** — Fast linting
- **Bandit** — Security vulnerability scanning

---

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **E2E Testing** | Playwright, pytest, pytest-xdist, pytest-playwright |
| **Performance** | Locust (HTTP load testing) |
| **Containerization** | Docker (multi-stage builds) |
| **Orchestration** | Kubernetes (manifests, CronJobs) |
| **CI/CD** | GitHub Actions (matrix strategy) |
| **Monitoring** | Prometheus, Grafana |
| **Reporting** | Allure Framework |
| **Code Quality** | Black, isort, mypy, Ruff, Bandit, pre-commit |
| **Configuration** | Pydantic Settings |
| **Visual Testing** | TBD (Tier 2) |
| **Accessibility** | TBD (Tier 2: axe-core-python) |
| **Cloud** | TBD (Tier 2: AWS EKS, ECR, S3) |
| **IaC** | TBD (Tier 2: Terraform) |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Docker (optional, for containerized execution)
- Node.js 16+ (for Playwright browsers)

### Local Setup

```bash
# 1. Clone repository
git clone https://github.com/your-username/multi-app-playwright-test-platform
cd multi-app-playwright-test-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install

# 4. Run tests
pytest tests/saucedemo/          # Run SauceDemo tests
pytest tests/ -n auto             # Run all tests in parallel
pytest -m smoke                   # Run smoke tests only

# 5. View Allure report
allure serve allure-results
```

### Docker Execution

```bash
# Build image
docker build -t playwright-tests .

# Run tests
docker run --rm playwright-tests pytest tests/

# Run with environment variables
docker run --rm \
  -e BROWSER=firefox \
  -e HEADLESS=true \
  playwright-tests pytest tests/saucedemo/
```

### Kubernetes Deployment

```bash
# Deploy to K8s
kubectl apply -f k8s/

# View test job logs
kubectl logs -f job/playwright-test-job

# Check status
kubectl get jobs
```
---

## Quality Standards

### Code Quality
- Zero linter errors (Black, Ruff, mypy)
- 100% type hint coverage
- Pre-commit hooks enforced
- Security scanning with Bandit

### Performance Targets
- Test suite execution < 30 minutes
- CI feedback < 10 minutes
- Docker image < 800MB
- Automated regression detection

### Infrastructure
- Kubernetes deployment
- Prometheus/Grafana monitoring
- Container security scanning
- Automated testing pipeline

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Project Status

**Current Phase:** Tier 1 Implementation

### Tier 1 (Core - In Progress)
- [x] Project structure and documentation
- [ ] Architecture design and ADRs
- [ ] SauceDemo test suite (E2E tests)
- [ ] The Internet test suite
- [ ] UI Playground test suite
- [ ] Docker containerization (<800MB)
- [ ] Kubernetes manifests (CronJobs, ConfigMaps)
- [ ] CI/CD pipeline (GitHub Actions, matrix strategy)
- [ ] Performance testing (Locust)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Allure reporting
- [ ] Pre-commit hooks and code quality

### Tier 2 (Planned - TBD)
- [ ] Visual regression testing
- [ ] Accessibility testing (axe-core)
- [ ] AWS deployment (EKS, ECR, S3)
- [ ] Terraform infrastructure
- [ ] Advanced monitoring and alerting
- [ ] Flaky test detection

### Tier 3 (Future - TBD)
- [ ] Smart test selection
- [ ] Test impact analysis
- [ ] Multi-cloud support
- [ ] Advanced security scanning
