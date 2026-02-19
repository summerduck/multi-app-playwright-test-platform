---
name: locust-performance-test
description: Generate Locust performance test scenarios for the multi-app test platform with app-specific HTTP flows, load shapes, threshold detection, and CI integration. Use when creating performance tests, load tests, stress tests, Locust scenarios, or when the user mentions Locust, performance testing, or load shapes.
---

# Locust Performance Test

Generate Locust HTTP performance scenarios for the project's target applications.

## Before Generating

1. Add `locust` to `requirements.txt` if not already present — it is **not currently included**
2. Check `conftest.py` `AppUrl` enum for target URLs
3. Review the roadmap (`.notes/roadmap.md` → Performance Testing section) for planned scope
4. Understand the constraint: these are **third-party public apps** with unknown rate limits

## Project Context

- **Target apps** (from `conftest.py` `AppUrl` enum):
  - SauceDemo: `https://www.saucedemo.com` — e-commerce demo, has login + inventory + cart + checkout flow
  - The Internet: `https://the-internet.herokuapp.com` — collection of isolated page examples
  - UI Playground: `http://uitestingplayground.com` — UI testing challenge pages
- **Planned directory:** `performance/` (from roadmap)
- **pytest marker:** `@pytest.mark.performance` is defined in `pyproject.toml` for any pytest-based performance tests; Locust scenarios run independently via `locust -f` and do not use pytest markers
- **Logging convention:** `logging.getLogger(__name__)` with `%s` formatting
- **Type hints:** Python 3.12+ syntax, must pass `mypy --strict`
- **Task runner:** `Taskfile.yml` — add `task perf` entry for running Locust

## Important Constraints

These are **third-party public applications** we do not control:
- They may have rate limiting, CDN caching, or anti-bot protection
- Aggressive load testing may get the CI IP blocked
- Keep concurrent users conservative (10-50 max) for routine CI runs
- Use higher loads only for local/manual investigation, not automated CI

Locust tests are HTTP-based — they do **not** use Playwright. They complement the Playwright E2E tests by measuring server response times under load, while Playwright tests verify UI behaviour.

## Directory Structure

```
performance/
├── __init__.py
├── locustfile.py              # Main entry point — imports all scenarios
├── scenarios/
│   ├── __init__.py
│   ├── saucedemo_scenarios.py # Login → inventory → cart → checkout flow
│   ├── theinternet_scenarios.py
│   └── uiplayground_scenarios.py
├── shapes/
│   ├── __init__.py
│   ├── ramp_up.py
│   └── spike.py
└── thresholds.py              # Per-endpoint regression thresholds
```

## SauceDemo Scenario

SauceDemo has the richest user flow: login → browse inventory → view product → add to cart → checkout. This maps directly to the Playwright page objects planned for `pages/saucedemo/`.

**SPA caveat:** SauceDemo is a client-side React app. The HTTP-based Locust requests below measure server response times and static asset delivery, not the JavaScript-rendered UI. Login via `POST` with form data may not replicate the actual client-side auth flow. Treat these as server-side baseline measurements — for full UI fidelity, use the Playwright E2E tests.

```python
"""SauceDemo performance scenarios.

HTTP-based load test — complements Playwright E2E tests by measuring
response times under concurrent load.
"""

import logging

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)


class SauceDemoUser(HttpUser):
    """Simulates a user browsing and purchasing on SauceDemo.

    Task weights reflect typical user behaviour:
    - Browsing (weight 3) is most common
    - Viewing products (weight 2) is frequent
    - Adding to cart + checkout (weight 1) is least common
    """

    host = "https://www.saucedemo.com"
    wait_time = between(1, 3)

    def on_start(self) -> None:
        """Log in before running tasks."""
        logger.info("Logging in as standard_user")
        self.client.post(
            "/",
            data={"user-name": "standard_user", "password": "secret_sauce"},
            name="login",
        )

    @task(3)
    def browse_inventory(self) -> None:
        """Browse the inventory page (most common action)."""
        self.client.get("/inventory.html", name="inventory")

    @task(2)
    def view_product(self) -> None:
        """View a product detail page."""
        self.client.get("/inventory-item.html?id=4", name="product-detail")

    @task(1)
    def add_to_cart_and_checkout(self) -> None:
        """Add item to cart and begin checkout (least common action)."""
        self.client.post("/cart.html", name="add-to-cart")
        self.client.get("/checkout-step-one.html", name="checkout")
```

## The Internet Scenario

The Internet is a collection of independent pages — no login flow. Test individual page loads:

```python
"""The Internet performance scenarios.

Each page is independent — no session state required.
"""

import logging

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)


class TheInternetUser(HttpUser):
    """Simulates browsing independent pages on The Internet."""

    host = "https://the-internet.herokuapp.com"
    wait_time = between(1, 3)

    @task(3)
    def load_homepage(self) -> None:
        """Load the main page with links to all examples."""
        self.client.get("/", name="homepage")

    @task(2)
    def load_dynamic_loading(self) -> None:
        """Load the dynamic loading example page."""
        self.client.get("/dynamic_loading", name="dynamic-loading")

    @task(2)
    def load_tables(self) -> None:
        """Load the sortable tables page."""
        self.client.get("/tables", name="tables")

    @task(1)
    def load_login_page(self) -> None:
        """Load the login form page."""
        self.client.get("/login", name="login-page")
```

## Load Shapes

### Ramp-Up

Conservative ramp for routine CI runs against public apps:

```python
"""Ramp-up load shape for CI performance checks."""

from locust import LoadTestShape


class RampUpShape(LoadTestShape):
    """Gradual ramp to target, hold, then ramp down.

    Conservative settings for third-party public apps.
    """

    target_users = 20
    ramp_up_time = 30       # seconds to reach target
    hold_time = 60          # seconds at target load
    ramp_down_time = 15     # seconds to wind down
    spawn_rate = 2          # users per second

    def tick(self) -> tuple[int, float] | None:
        run_time = self.get_run_time()

        if run_time < self.ramp_up_time:
            users = int(self.target_users * run_time / self.ramp_up_time)
            return max(users, 1), self.spawn_rate

        if run_time < self.ramp_up_time + self.hold_time:
            return self.target_users, self.spawn_rate

        if run_time < self.ramp_up_time + self.hold_time + self.ramp_down_time:
            elapsed = run_time - self.ramp_up_time - self.hold_time
            remaining = 1 - elapsed / self.ramp_down_time
            users = int(self.target_users * remaining)
            return max(users, 1), self.spawn_rate

        return None
```

### Spike (Local Investigation Only)

Higher load for local testing — do not run in CI against public apps:

```python
"""Spike load shape for local investigation only."""

from locust import LoadTestShape


class SpikeShape(LoadTestShape):
    """Sudden traffic burst for local performance investigation.

    WARNING: Do not use in CI against third-party public apps.
    """

    baseline_users = 5
    peak_users = 50
    warm_up_time = 15       # seconds
    spike_duration = 30     # seconds
    cool_down_time = 30     # seconds
    spawn_rate = 10         # users per second

    def tick(self) -> tuple[int, float] | None:
        run_time = self.get_run_time()

        if run_time < self.warm_up_time:
            return self.baseline_users, self.spawn_rate

        if run_time < self.warm_up_time + self.spike_duration:
            return self.peak_users, self.spawn_rate

        if run_time < self.warm_up_time + self.spike_duration + self.cool_down_time:
            return self.baseline_users, self.spawn_rate

        return None
```

## Performance Regression Thresholds

Per-endpoint thresholds for SauceDemo (the richest flow). These are initial baselines — adjust after collecting real data:

```python
"""Performance regression thresholds for SauceDemo endpoints.

Thresholds are conservative starting points. Update after collecting
baseline data from multiple runs.
"""

SAUCEDEMO_THRESHOLDS: dict[str, dict[str, float]] = {
    "login": {
        "p95_response_time_ms": 2000,
        "error_rate_percent": 1.0,
    },
    "inventory": {
        "p95_response_time_ms": 1500,
        "error_rate_percent": 0.5,
    },
    "product-detail": {
        "p95_response_time_ms": 1500,
        "error_rate_percent": 0.5,
    },
    "checkout": {
        "p95_response_time_ms": 3000,
        "error_rate_percent": 1.0,
    },
}


def check_thresholds(
    stats: dict[str, dict[str, float]],
    thresholds: dict[str, dict[str, float]] = SAUCEDEMO_THRESHOLDS,
) -> list[str]:
    """Compare actual stats against thresholds.

    Returns:
        List of violation messages. Empty list means all thresholds passed.
    """
    violations: list[str] = []
    for endpoint, limits in thresholds.items():
        actual = stats.get(endpoint, {})
        for metric, limit in limits.items():
            value = actual.get(metric, 0.0)
            if value > limit:
                violations.append(
                    f"{endpoint}.{metric}: {value:.1f} exceeded {limit:.1f}"
                )
    return violations
```

## Main Locustfile Entry Point

```python
"""Main Locust entry point — imports all app scenarios.

Run: locust -f performance/locustfile.py
Run specific app: locust -f performance/locustfile.py --class-picker
"""

from performance.scenarios.saucedemo_scenarios import SauceDemoUser  # noqa: F401
from performance.scenarios.theinternet_scenarios import TheInternetUser  # noqa: F401
```

## Taskfile Integration

Add to `Taskfile.yml`:

```yaml
  # ============================================================================
  # Performance Testing
  # ============================================================================

  perf:
    desc: Run performance tests (headless, SauceDemo, 20 users, 2 min)
    cmds:
      - |
        locust -f performance/locustfile.py \
          --headless \
          --users 20 \
          --spawn-rate 2 \
          --run-time 120s \
          --csv=performance/results \
          --html=performance/report.html

  perf-ui:
    desc: Start Locust web UI for interactive performance testing
    cmds:
      - locust -f performance/locustfile.py
```

## CI Workflow Integration

Add as a job in `.github/workflows/tests.yml` (see github-actions-test-pipeline skill). Runs after E2E tests to avoid blocking the main matrix:

```yaml
  performance:
    name: Performance Baseline
    needs: e2e-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}
          restore-keys: pip-${{ runner.os }}-

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run Locust (headless, conservative)
        run: |
          locust -f performance/locustfile.py \
            --headless \
            --users 20 \
            --spawn-rate 2 \
            --run-time 120s \
            --csv=performance/results \
            --html=performance/report.html

      - name: Upload performance results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: performance-results
          path: |
            performance/results*.csv
            performance/report.html
          retention-days: 30
```

## Rules

- Each app gets its own scenario file in `performance/scenarios/`
- `name=` parameter on every `self.client` call — these names are used in thresholds and reports
- `wait_time = between(1, 3)` — simulate realistic think time between requests
- `@task(weight)` — distribute traffic to match real user behaviour patterns
- `on_start()` for authentication (SauceDemo) — other apps may not need it
- Conservative user counts for CI (max 20) — these are public third-party apps
- Spike shapes for local investigation only — never in automated CI
- Add `locust` to `requirements.txt` before generating (it is not currently included)
- `logging.getLogger(__name__)` for scenario logging, `%s` formatting
- Type-hint all functions with Python 3.12+ syntax
- Thresholds are starting points — update after collecting baseline data
- Cross-reference: Locust HTTP endpoints should match `URL_PATH` values from page objects
