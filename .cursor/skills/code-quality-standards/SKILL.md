---
name: code-quality-standards
description: Project Python code quality rules enforced by ruff, mypy, and bandit (pyproject.toml). Use when generating or reviewing any Python file — page objects, tests, workflows, conftest, Locust scenarios — to ensure generated code passes pre-commit hooks without modification.
---

# Code Quality Standards

Rules derived from `pyproject.toml`. All generated Python files must pass `ruff`, `mypy --strict`, and `bandit` without modification.

## Tools at a Glance

| Tool | Config key | What it enforces |
|------|------------|-----------------|
| `ruff format` | `line-length = 88` | Formatting, line length |
| `ruff lint` | `select = [E,F,I,N,UP,B,C4,SIM,RET,ARG,PTH,ERA,PL]` | Style, imports, bugs, simplifications |
| `mypy` | `strict = true` | Full type annotations |
| `bandit` | `severity = "medium"` | Security issues |

---

## Import Order (rule `I` — isort)

`known-first-party = ["pages", "tests", "utils", "config"]`

Three groups, blank line between each, alphabetical within each group:

```python
# 1. stdlib
import logging
from pathlib import Path
from typing import Self

# 2. Third-party
import allure
import pytest
from locust import HttpUser, between, task
from playwright.sync_api import Locator, Page, expect

# 3. First-party — alphabetical: config < pages < tests < utils
from config.data.models import User
from config.data.saucedemo import SauceDemoUser
from pages.saucedemo.inventory_page import InventoryPage
from pages.saucedemo.login_page import LoginPage
```

**Rules:**
- No imports inside functions or methods — top-level only
- `from package import module as alias` — not `from package.module as alias` (invalid syntax)
- `performance/` is **not** first-party — Locust files have no first-party imports

---

## Type Annotations (mypy `strict = true`)

Every function and method must be fully annotated — no exceptions outside of test fixtures (which are exempt via `ARG`).

### Required patterns

```python
# Functions
def check_thresholds(
    stats: dict[str, dict[str, float]],
    thresholds: dict[str, dict[str, float]] = SAUCEDEMO_THRESHOLDS,
) -> list[str]: ...

# Methods — chaining
def fill_form(self, data: CheckoutInfo) -> Self: ...

# Methods — void
def test_login(self, login_page: LoginPage) -> None: ...

# Hooks
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None: ...

# LoadTestShape
def tick(self) -> tuple[int, float] | None: ...
```

### Modern Python 3.12 syntax (rule `UP`)

| ❌ Old | ✅ New |
|--------|--------|
| `Optional[str]` | `str \| None` |
| `Union[str, int]` | `str \| int` |
| `List[str]` | `list[str]` |
| `Dict[str, int]` | `dict[str, int]` |
| `Tuple[int, float]` | `tuple[int, float]` |
| `from typing import List, Dict, Optional` | remove — built-ins are generic |

`Self` still comes from `typing` (Python 3.11+).

---

## Ruff Rules Reference

### `B` — flake8-bugbear

**B006 — No mutable default arguments:**

```python
# Bad
def add_items(self, products: list[Product] = []) -> Self: ...

# Good — define inside body
def add_items(self, products: list[Product] | None = None) -> Self:
    if products is None:
        products = []
    ...
```

### `PTH` — use pathlib

```python
# Bad
import os
env_file = os.path.join(allure_dir, "environment.properties")
with open(env_file, "w") as f: ...

# Good
from pathlib import Path
env_file = Path(allure_dir) / "environment.properties"
env_file.write_text(...)
```

### `ERA` — no commented-out code

Remove dead code entirely. Use git history to recover if needed.

### `RET` — consistent returns

```python
# Bad — implicit None return mixed with explicit
def tick(self) -> tuple[int, float] | None:
    if run_time < 30:
        return 10, 2.0
    # falls off — implicit None, mypy also flags this

# Good
def tick(self) -> tuple[int, float] | None:
    if run_time < 30:
        return 10, 2.0
    return None
```

### `SIM` — simplify

```python
# Bad
if condition:
    return True
else:
    return False

# Good
return condition
```

### `ARG` — no unused arguments

Unused parameters cause lint failures in `pages/`, `utils/`, `config/`, `workflow/`, `performance/`.

Exempt files (per `pyproject.toml`):
- `tests/*` — fixtures often have side effects; unused params are normal
- `conftest.py` — pytest hook signatures are fixed

### `N` — pep8 naming

- Classes: `UpperCamelCase`
- Functions/methods/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private attributes: `_single_underscore` prefix

### `PL` — pylint (active subset)

| Ignored | Reason |
|---------|--------|
| `PLR0913` | Too many arguments — disabled (POM constructors have many params) |
| `PLR2004` | Magic values — disabled globally; also exempt in `tests/*` |

---

## Bandit (security)

The pre-commit bandit hook has `exclude: ^tests/` — bandit does **not** run on `tests/` at all.

For all other code (`pages/`, `utils/`, `config/`, `workflow/`):
- `B101` (assert_used) is skipped globally via `pyproject.toml` — so `assert` won't fail bandit
- However, do not use bare `assert` in `pages/` or `workflow/`: asserts are disabled by Python's `-O` optimisation flag and provide no auto-waiting — use `expect()` instead

```python
# Bad — in pages/
def verify_loaded(self) -> Self:
    assert self._page.url == "/inventory.html"  # disabled with python -O, no auto-wait

# Good — in pages/
def verify_loaded(self) -> Self:
    expect(self._page).to_have_url("/inventory.html")  # auto-waits, clear error on failure
    return self
```

---

## Per-File Exemptions (from `pyproject.toml`)

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*"      = ["ARG", "PLR2004"]
"conftest.py"  = ["ARG"]
```

| Location | Exempt rules | Why |
|----------|-------------|-----|
| `tests/*` | `ARG`, `PLR2004` | Fixtures have side effects; magic numbers in assertions |
| `conftest.py` | `ARG` | Hook signatures are defined by pytest — params can't be removed |
| All other | none | Full linting applies |

---

## Pre-Generation Checklist

Before finalising any generated Python file:

- [ ] Imports: stdlib → third-party → first-party, alphabetical within each group
- [ ] No imports inside functions or methods
- [ ] Every `def` has full parameter and return type annotations
- [ ] No `Optional`, `List`, `Dict`, `Tuple` — use `X | None`, `list`, `dict`, `tuple`
- [ ] No mutable default arguments
- [ ] `pathlib.Path` instead of `os.path` or bare `open()`
- [ ] No commented-out code
- [ ] Every branch returns consistently (`RET`)
- [ ] `assert` only in `test_*.py` / `conftest.py` — `expect()` everywhere else
- [ ] All logging uses `%s` format: `logger.info("msg: %s", value)` — not f-strings
