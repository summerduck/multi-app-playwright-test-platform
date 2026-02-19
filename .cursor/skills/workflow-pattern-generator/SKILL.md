---
name: workflow-pattern-generator
description: Generate Workflow classes that orchestrate multiple page objects into reusable end-to-end business flows with Allure step decorators, full type hints, structured logging, and method chaining. Use when creating workflows, end-to-end flows, business processes, user journeys, or orchestration layers for saucedemo, theinternet, or uiplayground apps.
---

# Workflow Pattern Generator

Generate workflow classes that orchestrate page objects into multi-step business flows.

This skill complements:
- **playwright-page-object-generator** — page objects that workflows consume
- **pytest-test-scaffolder** — test files that consume workflows via fixtures
- **allure-report-enhancer** — report hierarchy (`@allure.step()` placement on workflow methods)

## Before Generating

1. Identify the target app: `saucedemo`, `the_internet`, or `ui_playground`
2. Check existing page objects in `pages/<app>/` — workflows can only orchestrate pages that exist
3. Check existing workflows in `workflow/` to avoid duplication
4. Read `config/data/` for relevant data models (`User`, `Product`, `CheckoutInfo`)
5. Read `pages/<app>/<app>_base_page.py` to understand available domain methods

## File Placement

```
workflow/
├── __init__.py
├── saucedemo_workflow.py
├── the_internet_workflow.py
└── ui_playground_workflow.py
```

File naming: `<app>_workflow.py` — one workflow class per app.

## Architecture

Workflows sit between the test layer and the page object layer, orchestrating
multi-page flows so tests stay focused on assertions:

```
Test Layer (tests/<app>/)
  │  consumes workflow via fixture
  │
  └── Workflow Layer (workflow/<app>_workflow.py)
        │  creates and coordinates page objects
        │
        └── Page Object Layer (pages/<app>/)
              │  interacts with browser
              │
              └── Playwright Page
```

### How It Fits the Existing POM

| Layer | Responsibility | Assertions? |
|-------|---------------|-------------|
| Test | Assert outcomes, provide test data via parametrize | Yes |
| Workflow | Orchestrate multi-page flows, compose page objects | No |
| Page Object (Tier 3) | Single-page actions and getters | No |
| Domain Base (Tier 2) | Shared app-level components | No |
| BasePage (Tier 1) | Navigation, screenshots | No |

### When to Use a Workflow vs. Direct Page Object Calls

**Use a workflow when:**
- The flow spans 2+ pages (login -> inventory -> cart -> checkout)
- The same multi-step sequence is reused across 3+ tests
- The business process has conditional branching (e.g., guest vs. authenticated checkout)

**Use page objects directly when:**
- The test exercises a single page
- The flow is unique to one test
- You need fine-grained control over individual steps for assertion

## Conventions

| Aspect | Convention |
|--------|-----------|
| Constructor | `(page: Page, base_url: str)` — same signature as page objects |
| Page object creation | Internal, within methods — workflows own the orchestration |
| Methods | `@allure.step()` on every public method |
| Return type (chaining) | `Self` from `typing` for method chaining |
| Return type (handoff) | Next page object type when handing control back to the test |
| Return type (data) | Concrete type (`str`, `int`, `float`) for getters |
| Logging | Module-level `logger = logging.getLogger(__name__)` |
| Type hints | Full annotations on all parameters and return types |
| Data params | Accept `config.data.models` dataclasses, not raw strings |
| Docstrings | Google-style; document Args, Returns |
| No assertions | Workflows never assert — tests own the assertion layer |
| No exposed internals | Never expose internal page objects via public attributes |

## Workflow Template

File: `workflow/<app>_workflow.py`

```python
"""<App> workflow — end-to-end business flows for <App>."""

import logging
from typing import Self

import allure
from playwright.sync_api import Page

from config.data.models import User
from pages.<app>.login_page import LoginPage
from pages.<app>.inventory_page import InventoryPage

logger = logging.getLogger(__name__)


class <App>Workflow:
    """Orchestrates multi-page flows across <App>.

    Creates page objects internally and coordinates their interactions
    to represent complete user journeys. Tests consume this via a
    pytest fixture — never instantiate directly in test code.
    """

    def __init__(self, page: Page, base_url: str) -> None:
        self._page = page
        self._base_url = base_url
        self._login_page = LoginPage(self._page, self._base_url)

    @allure.step("Perform <business flow>")
    def <flow_method>(self, ...) -> Self:
        """Execute the complete <business flow>.

        Args:
            ...: Flow-specific parameters.

        Returns:
            Self for method chaining.
        """
        logger.info("Workflow: performing <business flow>")
        # Orchestrate the multi-step flow
        return self
```

## Test Consumption

### With Workflow (concise, intent-focused)

```python
    def test_purchase_backpack(
        self, saucedemo_workflow: SauceDemoWorkflow
    ) -> None:
        """Verify a standard user can complete a purchase."""
        # Arrange + Act
        saucedemo_workflow.purchase_items(
            user=SauceDemoUser.STANDARD,
            products=[SauceDemoProduct.BACKPACK],
            checkout_info=SauceDemoCheckout.VALID,
        )

        # Assert
        # (same assertions)
```

### Without Workflow (verbose, same flow inlined)

```python
    def test_purchase_backpack(
        self,
        login_page: LoginPage,
        inventory: InventoryPage,
        cart: CartPage,
        checkout: CheckoutPage,

    ) -> None:
        """Same test without workflow — more verbose."""
        # Arrange
        login_page.navigate()
        login_page.login_as(SauceDemoUser.STANDARD)

        # Act
        inventory.add_to_cart(SauceDemoProduct.BACKPACK)
        inventory.go_to_cart()
        cart.proceed_to_checkout()
        checkout.fill_info(SauceDemoCheckout.VALID).finish()

        # Assert
        # (same assertions)
```

The workflow version is shorter and expresses business intent. The Allure report
still shows every page-level step because workflow methods call page object methods
that carry their own `@allure.step()` decorators.

### Mixing Workflows and Page Objects

A test can use a workflow for setup and a page object for the action under test:

```python
    def test_cart_shows_added_items(
        self,
        saucedemo_workflow: SauceDemoWorkflow,
        products=[SauceDemoProduct.BACKPACK, SauceDemoProduct.BIKE_LIGHT]
    ) -> None:
        """Verify cart displays items added via workflow."""
        # Arrange — workflow handles login + add-to-cart
        saucedemo_workflow.add_items_to_cart(
            user=SauceDemoUser.STANDARD,
            products=products,
        )

        # Assert — interact with cart page object directly
        cart.verify_cart_contents(expected_products=products)
```

## Rules

### Do
- Create page objects internally within the workflow class (`__init__` for shared pages, inside methods for page-specific ones) — never expose them as public attributes
- Decorate every public method with `@allure.step()`
- Return `Self` for chaining, a page object for handoff, or a concrete type for getters
- Accept `config.data.models` dataclasses, not raw strings
- Log the high-level flow with `logger.info()`
- Compose existing page object methods — do not bypass POM to touch `self._page` directly
- Provide workflows to tests via fixtures in `tests/<app>/conftest.py`

### Do not
- Include assertions in workflows — tests own the assertion layer
- Expose internal page objects via public attributes or properties
- Hard-code credentials, product names, or URLs
- Use `time.sleep()` — Playwright auto-waiting propagates through page objects
- Use `with allure.step()` — use the `@allure.step()` decorator
- Instantiate workflows directly in tests — provide them via fixtures
- Duplicate page object logic — call page object methods, do not reimplement them
