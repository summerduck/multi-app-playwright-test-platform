---
name: playwright-page-object-generator
description: Generate Playwright Page Object classes following project conventions with BasePage inheritance, Allure step decorators, full type hints, structured logging, and method chaining. Use when creating new page objects, building POM classes, or scaffolding page layers for saucedemo, theinternet, or uiplayground apps.
---

# Playwright Page Object Generator

Generate page object classes that match the project's exact conventions across 3 apps.

## Why Use Page Object Model?

### Benefits

✅ **Separation of Concerns**: UI interactions separated from test logic
✅ **Reusability**: Page methods can be reused across multiple tests
✅ **Maintainability**: Locator changes only affect one place
✅ **Readability**: Tests read like business scenarios
✅ **Reduced Duplication**: DRY principle applied to UI interactions
✅ **Type Safety**: IDE autocomplete and type checking support

### Problems It Solves

❌ **Fragile Tests**: Locator changes break multiple tests
❌ **Code Duplication**: Same UI interactions written repeatedly
❌ **Poor Readability**: Tests filled with technical implementation details
❌ **Difficult Maintenance**: Changes require updates in multiple places


This skill complements:
- **pytest-test-scaffolder** — test files that consume page objects via fixtures
- **allure-report-enhancer** — report hierarchy (`@allure.step()` placement on POM methods)

## Before Generating

1. Identify the target app: `saucedemo`, `the_internet`, or `ui_playground`
2. Check existing page objects in `pages/<app>/`
3. Read `pages/base_page.py` for available Tier 1 base methods
4. Read `pages/<app>/<app>_base_page.py` for available Tier 2 domain methods
5. Check `config/data/` for relevant data models (`User`, `Product`, `CheckoutInfo`, `CreditCard`)
6. Check the target app's `base_url` fixture in `tests/<app>/conftest.py`

## File Placement

```
pages/
├── base_page.py                          # Tier 1: Universal base
├── saucedemo/
│   ├── __init__.py
│   ├── saucedemo_base_page.py            # Tier 2: Domain base
│   ├── login_page.py                     # Tier 3: Concrete page
│   ├── inventory_page.py
│   ├── cart_page.py
│   └── checkout_page.py
├── the_internet/
│   ├── __init__.py
│   ├── the_internet_base_page.py         # Tier 2: Domain base
│   ├── dynamic_loading_page.py
│   ├── file_upload_page.py
│   └── tables_page.py
└── ui_playground/
    ├── __init__.py
    ├── ui_playground_base_page.py         # Tier 2: Domain base
    ├── dynamic_id_page.py
    └── class_attribute_page.py
```

File naming: `<feature>_page.py` for concrete pages, `<app>_base_page.py` for domain bases.

## Architecture

3-tier POM: **BasePage → Domain Base Page → Concrete Page**

```
Tier 1: BasePage (pages/base_page.py)
  │     navigate(), take_screenshot()
  │
  ├── Tier 2: SauceDemoBasePage (pages/saucedemo/saucedemo_base_page.py)
  │     │     open_sidebar(), logout(), go_to_cart(), get_cart_badge_count(), reset_app_state()
  │     │
  │     ├── Tier 3: LoginPage
  │     ├── Tier 3: InventoryPage
  │     ├── Tier 3: CartPage
  │     └── Tier 3: CheckoutPage
  │
  ├── Tier 2: TheInternetBasePage (pages/the_internet/the_internet_base_page.py)
  │     │     get_page_heading(), get_footer_text()
  │     │
  │     ├── Tier 3: DynamicLoadingPage
  │     ├── Tier 3: FileUploadPage
  │     └── Tier 3: TablesPage
  │
  └── Tier 2: UIPlaygroundBasePage (pages/ui_playground/ui_playground_base_page.py)
        │     go_home(), get_navbar_brand()
        │
        ├── Tier 3: DynamicIdPage
        └── Tier 3: ClassAttributePage
```

| Tier | Scope | Contains |
|------|-------|----------|
| 1 — BasePage | All apps, all pages | Navigation, Allure screenshot |
| 2 — Domain Base | One app, all pages | Shared UI components (sidebar, navbar, header) |
| 3 — Concrete Page | One app, one page | Page-specific locators and actions |

Page objects are provided to tests via fixtures in `tests/<app>/conftest.py`. Tests never instantiate page objects directly.

## Conventions

| Aspect | Convention |
|--------|-----------|
| Locators | Private (`_` prefix), typed `Locator`, defined in `__init__`, prefer `data-test` / semantic selectors |
| Methods | `@allure.step()` on every public method |
| Return type | Always `Self` — page objects never instantiate other page objects |
| Logging | Module-level `logger = logging.getLogger(__name__)`; log actions, never sensitive data |
| Type hints | Full annotations on all parameters and return types |
| Data params | Accept `config.data.models` dataclasses (`User`, `Product`, etc.), not raw strings |
| Docstrings | Google-style; document Args, Returns, Raises where applicable |
| Class attribute | `URL_PATH` — relative path for `navigate()` |

## Tier 1 — BasePage Template

File: `pages/base_page.py` — app-agnostic, browser-level helpers only.

```python
"""Base page object — shared helpers for all page objects."""

import logging
from typing import Self

import allure
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BasePage:
    """Universal base class for all page objects across all apps.

    Attributes:
        URL_PATH: Override in subclasses with the page's relative path.
    """

    URL_PATH = "/"

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url

    @allure.step("Navigate to {self.URL_PATH}")
    def navigate(self) -> Self:
        """Open the page by navigating to base_url + URL_PATH."""
        url = f"{self._base_url}{self.URL_PATH}"
        logger.info("Navigating to: %s", url)
        self._page.goto(url)
        return self

    @allure.step("Take screenshot '{name}'")
    def take_screenshot(self, name: str = "screenshot") -> bytes:
        """Capture a screenshot and attach it to the Allure report."""
        screenshot = self._page.screenshot()
        allure.attach(
            screenshot, name=name, attachment_type=allure.attachment_type.PNG
        )
        return screenshot
```

## Tier 2 — Domain Base Page Template

File: `pages/<app>/<app>_base_page.py` — app-specific shared UI components.

Each domain base inherits `BasePage` and adds locators/methods for UI elements
shared across all (or most) pages within that app. Concrete pages inherit these
for free without re-defining them.

Playwright locators are lazy — they only query the DOM on interaction. A concrete
page that doesn't use an inherited locator (e.g. LoginPage inheriting burger menu
locators from SauceDemoBasePage) incurs no runtime cost or errors.

```python
"""<App> domain base page — shared components across <App> pages."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from pages.<app> import locators as loc

logger = logging.getLogger(__name__)


class <App>BasePage(BasePage):
    """Shared base for all <App> page objects.

    Encapsulates <shared UI description> that appear across <App> pages.
    """

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Shared locators ───────────────────────────────────────────
        self._shared_element: Locator = page.locator(loc.SHARED_ELEMENT)

    @allure.step("Interact with shared element")
    def shared_action(self) -> Self:
        """Perform an action on the shared element."""
        logger.info("Performing shared action")
        self._shared_element.click()
        return self
```

## Tier 3 — Concrete Page Template

File: `pages/<app>/<feature>_page.py` — inherits from the **domain base**, not `BasePage`.

```python
"""<App> <feature> page object."""

import logging
from typing import Self

import allure
from playwright.sync_api import Locator, Page, expect

from pages.<app>.<app>_base_page import <App>BasePage
from pages.<app> import locators as loc

logger = logging.getLogger(__name__)


class <Feature>Page(<App>BasePage):
    """Represents the <App> <feature> screen.

    Attributes:
        URL_PATH: Path to the <feature> page.
    """

    URL_PATH = "/<path>"

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        # ── Locators ─────────────────────────────────────────────────────
        self._example_input: Locator = page.locator(loc.example_input)
        self._submit_button: Locator = page.locator(loc.submit_button)
        self._error_message: Locator = page.locator(loc.error_message)

    # ── Actions ──────────────────────────────────────────────────────────
    @allure.step("Fill example field with '{value}'")
    def fill_example(self, value: str) -> Self:
        """Fill the example input field."""
        logger.info("Filling example field: %s", value)
        self._example_input.fill(value)
        return self

    @allure.step("Click submit button")
    def click_submit(self) -> Self:
        """Submit the form."""
        logger.info("Clicking submit button")
        self._submit_button.click()
        return self

    # ── Getters ──────────────────────────────────────────────────────────
    @allure.step("Get error message text")
    def get_error_message(self) -> str:
        """Return the text of the error banner."""
        logger.info("Getting error message text")
        return self._error_message.inner_text()

    @allure.step("Check if error message is visible")
    def is_error_visible(self) -> bool:
        """Return whether the error banner is displayed."""
        logger.info("Checking error message visibility")
        return self._error_message.is_visible()

    # ── Verification ─────────────────────────────────────────────────────
    @allure.step("Verify page is loaded")
    def verify_page_loaded(self) -> Self:
        """Assert the page is in the expected state using Playwright expect().

        Uses expect() for auto-waiting — never bare assert statements.
        """
        logger.info("Verifying page is loaded")
        expect(self._submit_button).to_be_visible()
        return self
```

## Cross-Page Navigation

Page object methods perform the action and return `Self`. The **test** (via fixtures)
owns the next page object — page objects never instantiate each other. This avoids
circular imports and keeps each page object independent.

```python
@allure.step("Log in as '{user}'")
def login_as(self, user: User) -> Self:
    """Fill credentials and submit the login form."""
    logger.info("Logging in as: %s", user)
    self.enter_username(user.username)
    self.enter_password(user.password)
    self.click_login()
    return self
```

```python
def test_login(login_page, inventory_page):
    login_page.navigate().
    login_page.login_as(valid_user)
    inventory_page.is_loaded()
```

## Composite Actions

Methods that accept data models group multiple field fills into a single user-facing action:

```python
from config.data.models import CheckoutInfo

@allure.step("Fill checkout info for '{info}'")
def fill_info(self, info: CheckoutInfo) -> Self:
    """Fill the checkout shipping form."""
    logger.info("Filling checkout info: %s", info)
    self._first_name_input.fill(info.first_name)
    self._last_name_input.fill(info.last_name)
    self._postal_code_input.fill(info.postal_code)
    return self
```

## Sensitive Data Handling

Never log passwords or card numbers. Omit the value from `@allure.step` titles:

```python
@allure.step("Enter password")
def enter_password(self, password: str) -> Self:
    """Fill the password field (value not logged for security)."""
    logger.info("Entering password")
    self._password_input.fill(password)
    return self
```

## Conftest Fixture Integration

Page objects are provided to tests via fixtures in `tests/<app>/conftest.py`. Each app directory defines its own `base_url` fixture and page object fixtures:

```python
"""Pytest fixtures for <App> tests."""

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

Each app directory owns its base URL — no global enum or marker introspection needed. The `base_url` fixture overrides Playwright's built-in fixture, so `--base-url` CLI still works as a fallback.

## Locator Strategy

Prefer stable selectors in this order:

1. `data-test` attributes: `page.locator("[data-test='login-button']")`
2. Playwright role selectors: `page.get_by_role("button", name="Login")`
3. Playwright text selectors: `page.get_by_text("Add to cart")`
4. CSS selectors (last resort): `page.locator(".inventory_item_name")`

Avoid XPath and positional selectors (`nth-child`, index-based).

## Code Quality

Apply all rules from the **code-quality-standards** skill.

`pages/` has no lint exemptions — full ruff + mypy strict + bandit apply. Use `expect()` from `playwright.sync_api` in `verify_*` methods — never bare `assert`.

## Rules

### Do
- Inherit concrete pages from the **domain base** (`<App>BasePage`), not `BasePage` directly
- Define all locators as private `Locator` attributes in `__init__`
- Decorate every public method with `@allure.step()`
- Always return `Self` — page objects never instantiate other page objects
- Accept `config.data.models` dataclasses, not raw strings
- Log actions with `logger.info()`
- Use Playwright auto-waiting (`.fill()`, `.click()`, `.wait_for()`)
- Implement all UI verification as dedicated `verify_*` methods (e.g., `verify_page_loaded`) inside page objects — use `expect()` from `playwright.sync_api` inside them, never bare `assert` statements

### Do not
- Create test data inside page objects
- Expose raw locators via public methods or attributes
- Hard-code values (URLs, credentials, product names)
- Use `time.sleep()` — rely on Playwright auto-waiting
- Use `with allure.step()` in page objects — use the `@allure.step()` decorator
- Instantiate page objects in tests — provide them via `tests/<app>/conftest.py` fixtures
- Import inside methods — use top-level imports only
- Return other page object types — always return `Self`, let tests own the next page


---

### ❌ DON'T

**1. Expose Raw Locators**
```python
# Bad: Exposes implementation details
def get_submit_button(self) -> Locator:
    return self.submit_button
```

**2. Use `assert` in Page Objects**
```python
# Bad: bare assert in page objects — no auto-waiting, breaks on timing
def login(self, email: str, password: str) -> None:
    self.email_input.fill(email)
    self.password_input.fill(password)
    self.submit_button.click()
    assert self.page.url == "/dashboard"  # Don't do this!

# Good: verify_* methods use expect() — auto-waiting, belongs in the page layer
from playwright.sync_api import expect
def verify_redirected_to_dashboard(self) -> Self:
    expect(self._page).to_have_url("/dashboard")
    return self
```

**3. Mix Concerns**
```python
# Bad: Page object shouldn't create test data
def create_reservation(self) -> None:
    credit_card = CreditCard(...)  # Don't create data here
    self.input_credit_card(credit_card)
```

**4. Use Hard-Coded Values**
```python
# Bad: Hard-coded values
def fill_form(self) -> None:
    self.name_input.fill("Test User")  # Don't hard-code

# Good: Accept parameters
def fill_form(self, name: str) -> None:
    self.name_input.fill(name)
```

---

## Common Anti-Patterns to Avoid

### Anti-Pattern 1: God Object

```python
# Bad: Single massive page object
class BookingFormPage:
    # 500+ lines handling all booking form pages
    def navigate(self): ...
    def select_menu(self): ...
    def input_payment(self): ...
    # ... 50 more methods
```

**Solution:** Split into focused page objects per page/component.


### Anti-Pattern 2: Leaking Implementation

```python
# Bad: Test knows about page structure
def test_login(login_page):
    login_page.page.locator("#email").fill("user@example.com")
    login_page.page.locator("#password").fill("password")
```

**Solution:** Encapsulate all page interactions in page object methods.
