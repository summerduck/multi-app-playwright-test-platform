---
name: allure-report-enhancer
description: Ensure every test has proper Allure annotations for professional reports — epics, features, stories, severity, steps, dynamic titles, attachments on failure, links, tags, and environment configuration. Use when adding Allure annotations, improving report quality, reviewing test metadata, or setting up Allure report configuration.
---

# Allure Report Enhancer

Ensure every test produces a professional, navigable Allure report with complete metadata.

## Why Use Allure Annotations?

### Benefits

✅ **Navigable Reports**: Epics → Features → Stories tree makes failures easy to locate
✅ **Severity Prioritization**: Triage by BLOCKER/CRITICAL/NORMAL/MINOR in CI dashboards
✅ **Step-Level Visibility**: Every POM action appears as a named step — no guessing what failed
✅ **Traceability**: Links connect tests to the app under test and issue tracker
✅ **Dynamic Titles**: Parametrized tests get human-readable names in the report
✅ **Automatic Attachments**: Screenshots and traces on failure without manual boilerplate

### Problems It Solves

❌ **Opaque Failures**: Test names like `test_login[0]` give no context in CI
❌ **Flat Reports**: Without hierarchy, hundreds of tests become an unsorted list
❌ **Missing Context**: No severity means every failure looks equally urgent
❌ **Manual Screenshots**: Forgetting to attach debug artifacts on failure
❌ **Duplicate Steps**: Using `with allure.step()` in tests duplicates what POM already provides

This skill complements:
- **pytest-test-scaffolder** — basic `@allure.feature/story/severity/title` placement
- **playwright-page-object-generator** — `@allure.step()` on page object methods
- **conftest.py** — automatic screenshot/trace attachment on failure (already implemented)

## Before Generating

1. Identify the target app: `saucedemo`, `the_internet`, or `ui_playground`
2. Check existing test files in `tests/<app>/` for current annotation coverage
3. Review the epic mapping table below — epic must match the app marker
4. Read `tests/<app>/conftest.py` to confirm `pytest_runtest_makereport` hook handles failure artifacts
5. Check `pyproject.toml` addopts for `--alluredir=allure-report` (already configured)

## Report Hierarchy

Map the project's 3-app structure to the Allure tree:

```
Epic (app name)
  └── Feature (page or feature area)
        └── Story (user scenario)
              └── Test (specific case with severity + title)
                    └── Steps (page object actions via @allure.step)
```

### Epic Mapping (Fixed)

Every test class maps to exactly one app:

| App marker | Epic value | URL |
|------------|------------|-----|
| `@pytest.mark.saucedemo` | `@allure.epic("SauceDemo")` | `https://www.saucedemo.com` |
| `@pytest.mark.theinternet` | `@allure.epic("The Internet")` | `https://the-internet.herokuapp.com` |
| `@pytest.mark.uiplayground` | `@allure.epic("UI Playground")` | `http://uitestingplayground.com` |

Place `@allure.epic` on the **class**. If a file has standalone functions, place it on each function.

### Decorator Placement

| Decorator | Where | Maps to |
|-----------|-------|---------|
| `@allure.epic("SauceDemo")` | test class | App under test |
| `@allure.feature("Login")` | test class | Page or feature area |
| `@allure.story("Valid credentials")` | test method | User scenario |
| `@allure.severity(...)` | test method | Priority level |
| `@allure.title("...")` | test method | Human-readable name in report |
| `@allure.step("...")` | page object method only (never in tests) | Individual action |

### Conventions

| Aspect | Convention |
|--------|-----------|
| Epic | One per test class, must match app marker — `SauceDemo`, `The Internet`, or `UI Playground` |
| Feature | One per test class, maps to page or feature area (e.g., `Authentication`, `Checkout`) |
| Story | One per test method, maps to user scenario (e.g., `Successful login`) |
| Severity | Required on every test — `BLOCKER`, `CRITICAL`, `NORMAL`, or `MINOR` |
| Title | Static `@allure.title` for normal tests; `allure.dynamic.title()` for parametrized |
| Steps | `@allure.step()` decorator on POM methods only — never `with allure.step()` in tests |
| Description | `@allure.description` for multi-step flows; skip for self-explanatory tests |
| Links | `@allure.link` to connect tests to the target app URL |
| Tags | `@allure.tag` for cross-cutting concerns (optional) |
| Attachments | Automatic via `conftest.py` on failure; manual only for additional debug data |

### Example: Full Hierarchy

Tests receive page objects as **fixture parameters** (defined in `tests/<app>/conftest.py`). Tests never instantiate page objects directly.

```python
from config.data.saucedemo import SauceDemoUser
from pages.saucedemo.login_page import LoginPage

@allure.epic("SauceDemo")
@allure.feature("Authentication")
class TestLogin:

    @allure.story("Successful login")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Standard user can log in with valid credentials")
    @pytest.mark.saucedemo
    @pytest.mark.smoke
    def test_valid_login(self, login_page: LoginPage) -> None:
        # Arrange
        login_page.navigate()

        # Act
        inventory = login_page.login_as(SauceDemoUser.STANDARD)

        # Assert
        inventory.verify_page_loaded()

    @allure.story("Login error handling")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("Locked-out user sees error message")
    @pytest.mark.saucedemo
    @pytest.mark.regression
    def test_locked_user(self, login_page: LoginPage) -> None:
        ...
```

## Severity Mapping for This Project

| Level | SauceDemo examples | The Internet examples | UI Playground examples |
|-------|-------------------|----------------------|----------------------|
| `BLOCKER` | Login, checkout submit | Authentication | — |
| `CRITICAL` | Add to cart, form validation | File upload, dynamic loading | Dynamic ID, class attribute |
| `NORMAL` | Sorting, filtering | Tables, hover | Hidden layers |
| `MINOR` | Placeholder text, tooltips | Notification messages | — |

## Dynamic Annotations (for Parametrized Tests)

Static `@allure.title` cannot interpolate parametrize values. Use `allure.dynamic` inside the test body:

```python
from config.data.models import User
from config.data.saucedemo import SauceDemoUser
from pages.saucedemo.login_page import LoginPage

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
    ],
)
def test_login_errors(
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

## Steps — Page Object Only

All steps live in the Page Object layer via `@allure.step()` decorators. Each POM method **is** a step — the Allure report shows the full step tree automatically. Tests never use `with allure.step()` context managers; they call POM methods directly:

```python
from config.data.saucedemo import SauceDemoCheckout, SauceDemoProduct, SauceDemoUser
from pages.saucedemo.login_page import LoginPage

@allure.epic("SauceDemo")
@allure.feature("Checkout")
class TestPurchaseFlow:

    @allure.story("Complete purchase")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("Standard user can complete a purchase")
    @pytest.mark.saucedemo
    @pytest.mark.acceptance
    def test_purchase_flow(
        self,
        login_page: LoginPage,
        inventory: InventoryPage,
        cart: CartPage,
        checkout: CheckoutPage
    ) -> None:
        """Verify end-to-end purchase flow on SauceDemo."""
        # Arrange
        login_page.navigate()
        login_page.login_as(SauceDemoUser.STANDARD)

        # Act
        inventory.add_to_cart(SauceDemoProduct.BACKPACK)
        inventory.add_to_cart(SauceDemoProduct.BIKE_LIGHT)
        inventory.open_cart()
        cart.proceed_to_checkout()
        checkout.fill_info(SauceDemoCheckout.VALID).finish()

        # Assert
        checkout.verify_order_confirmation()
```

Every method called above (`navigate`, `login_as`, `add_to_cart`, etc.) is decorated with `@allure.step()` in its Page Object class, so the report shows each action as a named step without any test-level boilerplate.

## Test Descriptions

Add `@allure.description` for multi-step flows. Skip it for self-explanatory tests:

```python
@allure.description(
    "Verifies the complete SauceDemo checkout flow:\n"
    "1. Log in as standard user\n"
    "2. Add item to cart from inventory\n"
    "3. Fill shipping info\n"
    "4. Confirm order\n"
    "5. Verify confirmation page"
)
```

## Links and Traceability

Connect tests to the target apps and issue tracker:

```python
@allure.link("https://www.saucedemo.com", name="SauceDemo")
@allure.link("https://the-internet.herokuapp.com", name="The Internet")
@allure.link("http://uitestingplayground.com", name="UI Playground")
```

## Manual Attachments in Tests

The `conftest.py` `pytest_runtest_makereport` hook already captures screenshots to `test-logs/screenshots/` and traces to `test-logs/traces/` on failure, attaching both to Allure. Do not duplicate this.

For **additional** debugging data in specific tests:

```python
# Attach API response for comparison tests
allure.attach(
    json.dumps(api_data, indent=2),
    name="api-response",
    attachment_type=allure.attachment_type.JSON,
)

# Attach page HTML on complex failures
allure.attach(
    page.content(),
    name="page-html",
    attachment_type=allure.attachment_type.HTML,
)
```

## Environment and Categories Configuration

### environment.properties

Add a `pytest_sessionfinish` hook to `conftest.py` (alongside the existing hooks) to generate environment metadata for the Allure report:

```python
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write Allure environment properties after the test session."""
    allure_dir = session.config.getoption("--alluredir", default=None)
    if allure_dir:
        env_file = Path(allure_dir) / "environment.properties"
        env_file.write_text(
            f"Browser={session.config.getoption('--browser', default='chromium')}\n"
            "Python=3.12\n"
            "Playwright=1.51.0\n"
            f"Workers={session.config.getoption('-n', default='1')}\n"
            f"Reruns={1}\n"
        )
```

Note: `--alluredir=allure-report` is already configured in `pyproject.toml` addopts.

### categories.json

Create `allure-report/categories.json` to classify failures in the report:

```json
[
  {
    "name": "Playwright timeout — element not found",
    "matchedStatuses": ["broken"],
    "messageRegex": ".*Timeout.*waiting.*selector.*"
  },
  {
    "name": "Assertion failures",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*AssertionError.*"
  },
  {
    "name": "Target app unreachable",
    "matchedStatuses": ["broken"],
    "messageRegex": ".*(ConnectionError|TimeoutError|net::ERR).*"
  }
]
```

Copy this file into the allure results directory before generating the report. The `task allure-report` Taskfile command generates reports from `allure-report/`.

## Decorator Order Convention

Stack decorators in this order (outermost first):

```python
@allure.epic("SauceDemo")            # 1. Epic (class-level)
@allure.feature("Checkout")          # 2. Feature (class-level)
class TestCheckout:

    @allure.story("Complete purchase")  # 3. Story
    @allure.severity(...)               # 4. Severity
    @allure.title("...")                # 5. Title
    @allure.description("...")          # 6. Description (optional)
    @allure.tag("checkout", "e2e")      # 7. Tags (optional)
    @allure.link(...)                   # 8. Links (optional)
    @pytest.mark.saucedemo              # 9. App marker
    @pytest.mark.acceptance             # 10. Category marker
    @pytest.mark.parametrize(...)       # 11. Parametrize (optional, last)
    def test_method(self, ...) -> None:
        ...
```

## Annotation Audit Checklist

When reviewing or enhancing tests, verify every test has:

- [ ] `@allure.epic("AppName")` on the class — one of: `SauceDemo`, `The Internet`, `UI Playground`
- [ ] `@allure.feature("FeatureArea")` on the class
- [ ] `@allure.story("Scenario")` on each test method
- [ ] `@allure.severity(allure.severity_level.*)` on each test method
- [ ] `@allure.title("Human-readable title")` on each test (or `allure.dynamic.title` for parametrized)
- [ ] App marker (`@pytest.mark.saucedemo/theinternet/uiplayground`) matches the epic
- [ ] At least one category marker (`smoke`, `regression`, `acceptance`, etc.)
- [ ] No `with allure.step()` in tests — steps are handled by POM `@allure.step()` decorators
- [ ] Page objects received as fixtures (from `tests/<app>/conftest.py`), not instantiated in tests

## Rules

### Do
- Place `@allure.epic` and `@allure.feature` on every test class
- Place `@allure.story`, `@allure.severity`, and a title on every test method
- Match epic to the app marker: `saucedemo` → `"SauceDemo"`, `theinternet` → `"The Internet"`, `uiplayground` → `"UI Playground"`
- Use `allure.dynamic.title()` for parametrized tests — static `@allure.title` cannot interpolate params
- Use `allure.dynamic.severity()` inside parametrized tests when severity varies by case
- Add `@allure.description` for complex multi-step flows
- Follow the decorator order convention (see Decorator Order section above)
- Add `@allure.link` to connect test classes to the app under test

### Do not
- Use `with allure.step()` in tests — all steps belong in Page Object methods via `@allure.step()` decorators
- Instantiate page objects in tests — receive them as fixtures from `tests/<app>/conftest.py`
- Attach screenshots manually — `conftest.py` handles this on failure via `pytest_runtest_makereport`
- Put `@allure.step()` on test methods — steps are for POM methods only
- Mix epics within a single test class — one class = one app
- Skip severity — every test must declare its priority level
- Use static `@allure.title` on parametrized tests — it cannot interpolate params

---

### ❌ DON'T

**1. Use `with allure.step()` in Tests**
```python
# Bad: Manual step blocks in tests
def test_purchase(self, login_page: LoginPage) -> None:
    with allure.step("Navigate to login"):
        login_page.navigate()
    with allure.step("Log in"):
        login_page.login_as(SauceDemoUser.STANDARD)

# Good: POM methods are already @allure.step() decorated
def test_purchase(self, login_page: LoginPage) -> None:
    login_page.navigate()
    login_page.login_as(SauceDemoUser.STANDARD)
```

**2. Mismatch Epic and App Marker**
```python
# Bad: Epic says SauceDemo but marker says theinternet
@allure.epic("SauceDemo")
@allure.feature("Tables")
class TestTables:
    @pytest.mark.theinternet  # Mismatch!
    def test_sort(self): ...

# Good: Epic and marker are consistent
@allure.epic("The Internet")
@allure.feature("Tables")
class TestTables:
    @pytest.mark.theinternet
    def test_sort(self): ...
```

**3. Static Title on Parametrized Tests**
```python
# Bad: Static title shows the same name for all params
@allure.title("Login with invalid user")
@pytest.mark.parametrize("user", [SauceDemoUser.LOCKED_OUT, SauceDemoUser.PROBLEM])
def test_invalid_login(self, login_page, user): ...

# Good: Dynamic title interpolates params
@pytest.mark.parametrize("user", [
    pytest.param(SauceDemoUser.LOCKED_OUT, id="locked"),
    pytest.param(SauceDemoUser.PROBLEM, id="problem"),
])
def test_invalid_login(self, login_page, user):
    allure.dynamic.title(f"Login with {user} shows error")
    ...
```

**4. Manual Screenshot Attachment**
```python
# Bad: Duplicates conftest.py failure handling
def test_login(self, login_page: LoginPage, page: Page) -> None:
    try:
        login_page.navigate()
        login_page.login_as(SauceDemoUser.STANDARD)
    except Exception:
        allure.attach(page.screenshot(), name="failure", attachment_type=allure.attachment_type.PNG)
        raise

# Good: conftest.py handles failure screenshots automatically
def test_login(self, login_page: LoginPage) -> None:
    login_page.navigate()
    login_page.login_as(SauceDemoUser.STANDARD)
```

**5. Missing Severity**
```python
# Bad: No severity — makes triage impossible
@allure.story("Checkout flow")
@allure.title("User can complete purchase")
def test_purchase(self): ...

# Good: Severity declared
@allure.story("Checkout flow")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("User can complete purchase")
def test_purchase(self): ...
```

## Common Anti-Patterns to Avoid

### Anti-Pattern 1: Flat Report (No Hierarchy)

```python
# Bad: No epic or feature — all tests appear in a flat list
class TestLogin:
    @allure.title("Login works")
    def test_login(self): ...
```

**Solution:** Always add `@allure.epic` + `@allure.feature` on the class.

### Anti-Pattern 2: Duplicate Steps

```python
# Bad: Test wraps POM calls in allure.step — report shows nested duplicates
def test_login(self, login_page: LoginPage) -> None:
    with allure.step("Navigate"):
        login_page.navigate()  # navigate() already has @allure.step
```

**Solution:** Let POM `@allure.step()` decorators handle all step reporting.

### Anti-Pattern 3: Inconsistent Naming

```python
# Bad: Mixed naming conventions across test files
@allure.epic("Sauce Demo")       # file 1
@allure.epic("saucedemo")        # file 2
@allure.epic("SauceDemo App")    # file 3
```

**Solution:** Use the exact epic mapping: `SauceDemo`, `The Internet`, `UI Playground`.
