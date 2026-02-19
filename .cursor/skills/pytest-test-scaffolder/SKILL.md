---
name: pytest-test-scaffolder
description: Scaffold pytest test files following project conventions with AAA pattern, pytest markers, Allure decorators, parametrize, and conftest fixtures. Use when creating new test files, adding test cases, generating test classes, or scaffolding tests for saucedemo, theinternet, or uiplayground apps.
---

# Pytest Test Scaffolder

Generate test files that match the project's exact conventions across 3 apps.

## Why Use This Test Structure?

### Benefits

✅ **Fixture-Based Page Objects**: Tests receive ready-to-use page instances — no manual instantiation
✅ **Consistent AAA Pattern**: Every test follows Arrange/Act/Assert for readability
✅ **Rich Allure Reports**: Epics, features, stories, and severity on every test
✅ **Data-Driven**: Parametrized tests with `pytest.param(id=)` for clear test IDs
✅ **App Isolation**: Each app directory owns its `base_url` and fixtures
✅ **Strict Markers**: `--strict-markers` prevents typos from silently creating new markers

### Problems It Solves

❌ **Flaky Setup/Teardown**: Manual setup methods replaced by composable fixtures
❌ **Hard-Coded Data**: Raw strings in tests replaced by frozen dataclasses from `config.data`
❌ **Missing Metadata**: Tests without Allure annotations produce empty, unnavigable reports
❌ **Tight Coupling**: Tests that instantiate page objects directly break when constructors change
❌ **Inconsistent Structure**: Ad-hoc test organization makes reviews and onboarding slower

This skill complements:
- **playwright-page-object-generator** — page object classes that tests consume via fixtures
- **allure-report-enhancer** — Allure annotation conventions and report hierarchy

## Before Generating

1. Identify the target app: `saucedemo`, `the_internet`, or `ui_playground`
2. Check which Page Objects exist in `pages/<app>/`
3. Review existing tests in `tests/<app>/` for patterns already in use
4. Read `conftest.py` to confirm available fixtures and hooks

## File Placement

```
tests/
├── saucedemo/
│   ├── conftest.py              # Page object fixtures for saucedemo
│   ├── test_login.py
│   ├── test_inventory.py
│   ├── test_cart.py
│   └── test_checkout.py
├── the_internet/
│   ├── conftest.py              # Page object fixtures for the_internet
│   ├── test_dynamic_loading.py
│   ├── test_file_upload.py
│   └── test_tables.py
├── ui_playground/
│   ├── conftest.py              # Page object fixtures for ui_playground
│   ├── test_dynamic_id.py
│   └── test_class_attribute.py
└── framework/
    └── test_log_helpers.py
```

File naming: `test_<feature>.py` (configured in `pyproject.toml`: `python_files = "test_*.py"`).
Each app directory has a `conftest.py` that provides page object fixtures.

## Conventions

| Aspect | Convention |
|--------|-----------|
| File naming | `test_<feature>.py` — one file per feature or page area |
| Class naming | `Test<Feature>` — groups related scenarios |
| Test naming | `test_<scenario>` — descriptive, uses underscores |
| Page objects | Received as **fixture parameters** from `tests/<app>/conftest.py`, never instantiated |
| Test data | Frozen dataclasses from `config.data.*`, never hard-coded strings |
| Structure | AAA comments: `# Arrange` / `# Act` / `# Assert` |
| Markers | Exactly one app marker + at least one category marker per test |
| Allure | `@allure.epic` + `@allure.feature` on class; `@allure.story` + `@allure.severity` + title on method |
| Assertions | Prefer `expect()` for DOM elements; `assert` only for non-DOM values |
| Type hints | Full annotations on all parameters and return types |
| Logging | Module-level `logger = logging.getLogger(__name__)`; log complex test setup |
| Docstrings | Google-style on every test class and test method |

## Available Markers (from pyproject.toml)

Every test **must** have an app marker plus at least one category marker.

**App markers** (exactly one per test):
- `@pytest.mark.saucedemo` — tests in `tests/saucedemo/`
- `@pytest.mark.theinternet` — tests in `tests/the_internet/`
- `@pytest.mark.uiplayground` — tests in `tests/ui_playground/`

**Category markers** (one or more):
- `smoke` — quick smoke tests (used in PR fast-feedback workflow)
- `regression` — full regression tests
- `acceptance` — acceptance / end-to-end flows
- `validation` — form and input validation
- `ui_ux` — UI/UX tests
- `security` — security tests
- `accessibility` — accessibility tests
- `network` — network monitoring tests
- `account_creation` — account creation tests
- `slow` — slow running tests
- `performance` — performance tests
- `integration` — integration tests
- `property` — property-based tests (Hypothesis)
- `unit` — unit tests for framework code (no app marker needed)

Note: `--strict-markers` is enabled in `pyproject.toml` addopts. Misspelled markers will fail the test run.

## Available Fixtures

### Root-level fixtures (from root `conftest.py`)

| Fixture | Scope | What it provides | Source |
|---------|-------|------------------|--------|
| `page` | function | Playwright `Page` instance | pytest-playwright plugin |
| `base_url` | function | Base URL for the app under test | `tests/<app>/conftest.py` |
| `user_password` | function | Password from `--user-pw` CLI or `USER_PASSWORD` env var | root `conftest.py` |
| `browser_context_args` | session | Viewport 1280x720, locale `en-GB`, timezone `Europe/London` | root `conftest.py` |

### App-level fixtures (from `tests/<app>/conftest.py`)

Each app directory has its own `conftest.py` that provides **page object fixtures**. Tests never instantiate page objects directly — they receive them as fixture parameters.

| Fixture | Returns | Source |
|---------|---------|--------|
| `login_page` | `LoginPage(page, base_url)` | `tests/saucedemo/conftest.py` |
| `inventory_page` | `InventoryPage(page, base_url)` | `tests/saucedemo/conftest.py` |
| `cart_page` | `CartPage(page, base_url)` | `tests/saucedemo/conftest.py` |
| `checkout_page` | `CheckoutPage(page, base_url)` | `tests/saucedemo/conftest.py` |
| `dynamic_loading_page` | `DynamicLoadingPage(page, base_url)` | `tests/the_internet/conftest.py` |
| `file_upload_page` | `FileUploadPage(page, base_url)` | `tests/the_internet/conftest.py` |
| `dynamic_id_page` | `DynamicIdPage(page, base_url)` | `tests/ui_playground/conftest.py` |

Note: page objects are always received as **fixtures**. Methods that transition the user to another page still return `Self` — the next page object comes from a separate fixture parameter, not from the return value of a POM method.

### How `base_url` Works

Each app directory defines its own `base_url` fixture in `tests/<app>/conftest.py`:

```python
@pytest.fixture
def base_url() -> str:
    return "https://www.saucedemo.com"
```

This overrides Playwright's built-in `base_url` fixture at directory scope. No global enum or marker introspection needed — each app directory owns its URL. The `--base-url` CLI option still works as a manual override.

## App-Level Conftest Template

Each app directory has a `conftest.py` that provides the `base_url` fixture and page object fixtures. Every page object gets its own fixture:

```python
"""Pytest fixtures for <App> tests.

Provides the base URL and page object fixtures so tests receive
ready-to-use page instances without instantiating them directly.
"""

import pytest
from playwright.sync_api import Page

from pages.<app>.login_page import LoginPage
from pages.<app>.inventory_page import InventoryPage


@pytest.fixture
def base_url() -> str:
    """Base URL for the <App> application."""
    return "<app-base-url>"


@pytest.fixture
def login_page(page: Page, base_url: str) -> LoginPage:
    """Provide a LoginPage instance for the current test."""
    return LoginPage(page, base_url)


@pytest.fixture
def inventory_page(page: Page, base_url: str) -> InventoryPage:
    """Provide an InventoryPage instance for the current test."""
    return InventoryPage(page, base_url)
```

Each app directory owns its `base_url` and page object fixtures. Tests never instantiate page objects directly.

## Automatic Behaviours (from pyproject.toml addopts)

These run automatically — do not duplicate in test code or commands:
- `--reruns=1` — failed tests are retried once
- `--cov=pages --cov=utils --cov=config` — coverage collected on page objects and utilities
- `--alluredir=allure-report` — Allure results directory
- `--html=report.html` — HTML report generated
- `-v --tb=short` — verbose output, short tracebacks
- `--strict-markers` — undefined markers cause errors

## Test Data Models

Tests **must not** contain hardcoded credentials, product names, or form data. Use the frozen dataclasses from `config/data/`:

```
config/data/
├── models.py         # User, Product, CheckoutInfo, CreditCard
└── saucedemo.py      # SauceDemoUser, SauceDemoProduct, SauceDemoCheckout, SortOption
```

Import pattern:

```python
from config.data.saucedemo import SauceDemoUser, SauceDemoProduct, SauceDemoCheckout, SortOption
```

Available predefined data:

| Namespace | Constants | Type |
|-----------|-----------|------|
| `SauceDemoUser` | `STANDARD`, `LOCKED_OUT`, `PROBLEM`, `PERFORMANCE_GLITCH`, `ERROR`, `VISUAL` | `User` |
| `SauceDemoProduct` | `BACKPACK`, `BIKE_LIGHT`, `BOLT_TSHIRT`, `FLEECE_JACKET`, `ONESIE`, `RED_TSHIRT` | `Product` |
| `SauceDemoCheckout` | `VALID`, `EMPTY`, `MISSING_FIRST_NAME`, `MISSING_LAST_NAME`, `MISSING_POSTAL_CODE` | `CheckoutInfo` |
| `SortOption` | `NAME_ASC`, `NAME_DESC`, `PRICE_ASC`, `PRICE_DESC` | `StrEnum` |

Page object methods accept the dataclass, not raw strings. All POM methods return `Self`:

```python
# Page object signatures
def login_as(self, user: User) -> Self: ...
def add_to_cart(self, product: Product) -> Self: ...
def fill_info(self, info: CheckoutInfo) -> Self: ...
def sort_by(self, option: SortOption) -> Self: ...
```

## Test File Template

Tests receive page objects as **fixture parameters** (defined in the app-level `conftest.py`). Tests never instantiate page objects directly.

```python
"""Tests for <Feature> on <App>."""

import logging

import allure
import pytest
from playwright.sync_api import Page, expect

from config.data.saucedemo import SauceDemoUser
from pages.<app>.login_page import LoginPage

logger = logging.getLogger(__name__)


@allure.epic("<App Name>")
@allure.feature("<Feature Area>")
class Test<Feature>:
    """<Feature> test suite for <App>."""

    @allure.story("<User Story>")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("<Human-readable test title>")
    @pytest.mark.<app>
    @pytest.mark.smoke
    def test_<scenario>(self, login_page: LoginPage, inventory: InventoryPage) -> None:
        """<What this test verifies>."""

        # Arrange
        login_page.navigate()

        # Act
        login_page.login_as(SauceDemoUser.STANDARD)

        # Assert
        inventory.verify_page_loaded()
```

Prefer verification methods on the page object (`verify_page_loaded`, `get_error_message`) over raw `page`/`expect()` in tests.

## Parametrized Test Template

```python
    @allure.story("Login error messages")
    @pytest.mark.saucedemo
    @pytest.mark.regression
    @pytest.mark.parametrize(
        ("user", "expected_error"),
        [
            pytest.param(SauceDemoUser.LOCKED_OUT, "locked out", id="locked-user"),
            pytest.param(
                User(username="", password="secret_sauce"),
                "Username is required",
                id="empty-username",
            ),
            pytest.param(
                User(username="invalid_user", password="secret_sauce"),
                "do not match",
                id="invalid-user",
            ),
        ],
    )
    def test_login_error_messages(
        self,
        login_page: LoginPage,
        user: User,
        expected_error: str,
    ) -> None:
        """Verify error messages for invalid login attempts."""
        allure.dynamic.title(f"Login with '{user}' shows '{expected_error}'")
        allure.dynamic.severity(allure.severity_level.CRITICAL)

        # Arrange
        login_page.navigate()

        # Act
        login_page.login_as(user)

        # Assert
        login_page.get_error_message(expected_error)
```

## Standalone Function Template

For simpler test files that do not need a class:

```python
"""Tests for <feature> on <App>."""

import logging

import allure
import pytest

from pages.<app>.<page_name>_page import <PageName>Page

logger = logging.getLogger(__name__)


@allure.epic("<App Name>")
@allure.feature("<Feature Area>")
@allure.story("<User Story>")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("<Human-readable test title>")
@pytest.mark.<app>
@pytest.mark.smoke
def test_<scenario>(<page_name>_page: <PageName>Page) -> None:
    """<What this test verifies>."""
    # Arrange
    <page_name>_page.navigate()

    # Act
    <page_name>_page.some_action()

    # Assert
    <page_name>_page.verify_result()
```

## Rules

### Do
- One `@allure.epic` per test class — must match the app marker (see allure-report-enhancer skill)
- One `@allure.feature` per test class (maps to the page or feature area)
- One `@allure.story` per test method (maps to the user scenario)
- `@allure.severity` on every test
- `@allure.title` with a human-readable description (or `allure.dynamic.title` for parametrized)
- Always include the app marker **and** at least one category marker
- AAA comments: `# Arrange` / `# Act` / `# Assert`
- Prefer `expect()` from `playwright.sync_api` for auto-waiting assertions on DOM elements
- Use `expect(page).to_have_url()`, `expect(locator).to_have_text()`, `expect(locator).to_be_visible()`
- Use `@pytest.mark.parametrize` when testing 3+ variations of the same scenario
- Always use tuple unpacking: `("param_a", "param_b")`
- Always add `id=` to `pytest.param()` for readable test IDs
- Use `allure.dynamic.title()` inside the test body for parametrized tests

### Do not
- Use `assert` to check DOM elements — use `expect()` for auto-waiting assertions on DOM
- Instantiate page objects in tests — receive them as fixtures via app-level `conftest.py`
- Put page object logic in tests — keep it in `pages/`
- Use `time.sleep()` — rely on Playwright auto-waiting
- Hard-code URLs — always use `base_url` fixture
- Hard-code credentials, product names, or form data — use `config.data` dataclasses
- Share mutable state between tests
- Use setup/teardown methods — use pytest fixtures instead
- Capture screenshots manually — `conftest.py` handles failure artifacts automatically
- Use `with allure.step()` in tests — steps belong in page object methods via `@allure.step()` decorators
- Import inside test methods — use top-level imports only (except `dataclasses.replace()` for password overrides)

---

### ❌ DON'T

**1. Instantiate Page Objects in Tests**
```python
# Bad: Test creates page objects directly
def test_login(page: Page) -> None:
    login_page = LoginPage(page, "https://www.saucedemo.com")
    login_page.navigate()
```

**2. Hard-Code Test Data**
```python
# Bad: Raw strings instead of data models
def test_login(self, login_page: LoginPage) -> None:
    login_page.enter_username("standard_user")
    login_page.enter_password("secret_sauce")

# Good: Use frozen dataclasses
def test_login(self, login_page: LoginPage) -> None:
    login_page.login_as(SauceDemoUser.STANDARD)
```

**3. Use `with allure.step()` in Tests**
```python
# Bad: Manual step blocks in tests
def test_login(self, login_page: LoginPage) -> None:
    with allure.step("Navigate to login"):
        login_page.navigate()
    with allure.step("Log in"):
        login_page.login_as(SauceDemoUser.STANDARD)

# Good: POM methods are already @allure.step() decorated
def test_login(self, login_page: LoginPage) -> None:
    login_page.navigate()
    login_page.login_as(SauceDemoUser.STANDARD)
```

**4. Add Assertions in Wrong Layer**
```python
# Bad: Using page internals for assertions
def test_login(self, login_page: LoginPage, page: Page) -> None:
    login_page.navigate()
    login_page.login_as(SauceDemoUser.STANDARD)
    assert page.locator(".inventory_list").is_visible()  # Leaks page structure

# Good: Use page object verification methods
def test_login(self, login_page: LoginPage, inventory_page: InventoryPage) -> None:
    login_page.navigate()
    login_page.login_as(SauceDemoUser.STANDARD)
    inventory_page.verify_page_loaded()
```

**5. Missing Markers**
```python
# Bad: No app marker or category marker
@allure.story("Login")
def test_login(self, login_page: LoginPage) -> None:
    ...

# Good: Both app and category markers
@allure.story("Login")
@pytest.mark.saucedemo
@pytest.mark.smoke
def test_login(self, login_page: LoginPage) -> None:
    ...
```

## Common Anti-Patterns to Avoid

### Anti-Pattern 1: Test Knows Page Structure

```python
# Bad: Test reaches into page internals
def test_item_count(self, page: Page, inventory_page: InventoryPage) -> None:
    inventory_page.navigate()
    items = page.locator(".inventory_item")
    assert items.count() == 6
```

**Solution:** Expose a getter method on the page object (`get_item_count()`).

### Anti-Pattern 2: Shared Mutable State

```python
# Bad: Class-level state shared across tests
class TestCart:
    items_added = []

    def test_add_item(self, cart_page):
        self.items_added.append("Backpack")
        ...

    def test_verify_cart(self, cart_page):
        assert len(self.items_added) == 1  # Depends on test order
```

**Solution:** Each test is fully independent. Use fixtures for shared setup.

### Anti-Pattern 3: Parametrize Without IDs

```python
# Bad: No test IDs — report shows [0], [1], [2]
@pytest.mark.parametrize("user,error", [
    (SauceDemoUser.LOCKED_OUT, "locked out"),
    (User(username="", password="x"), "Username is required"),
])
def test_errors(self, login_page, user, error): ...

# Good: Named test IDs for readable reports
@pytest.mark.parametrize(
    ("user", "expected_error"),
    [
        pytest.param(SauceDemoUser.LOCKED_OUT, "locked out", id="locked-user"),
        pytest.param(User(username="", password="x"), "Username is required", id="empty-username"),
    ],
)
def test_errors(self, login_page, user, expected_error): ...
```
