"""Global pytest configuration for the multi-app Playwright test platform.

Provides:
- Environment and log directory setup (xdist-aware)
- Playwright browser context configuration
- Screenshot and trace capture on test failure with Allure attachment
- Per-test file logging
- App base URL resolution via markers
"""

import logging
import os
from collections.abc import Generator
from enum import StrEnum, unique
from typing import Any

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

from utils.log_helpers import (
    FAILED_LOG_DIR,
    LOG_DIR,
    SCREENSHOTS_DIR,
    TRACES_DIR,
    build_log_filename,
    clean_and_create_log_dirs,
    ensure_log_dirs_exist,
    get_last_element,
    sanitize_nodeid,
)

logger = logging.getLogger(__name__)


# ── App base URLs ────────────────────────────────────────────────────────────
@unique
class AppUrl(StrEnum):
    """Supported application base URLs, keyed by pytest marker name."""

    SAUCEDEMO = "https://www.saucedemo.com"
    THEINTERNET = "https://the-internet.herokuapp.com"
    UIPLAYGROUND = "http://uitestingplayground.com"


# ── CLI Options ──────────────────────────────────────────────────────────────
def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for the test suite."""
    parser.addoption(
        "--user-pw",
        action="store",
        help="USER_PASSWORD",
        default=os.getenv("USER_PASSWORD"),
    )


# ── Session Configuration ────────────────────────────────────────────────────
def pytest_configure(config: pytest.Config) -> None:
    """Load environment variables and prepare log directories.

    In xdist parallel mode, only the master process cleans directories.
    Worker processes just ensure they exist to avoid race conditions.
    """
    load_dotenv()

    if not hasattr(config, "workerinput"):
        clean_and_create_log_dirs()
    else:
        ensure_log_dirs_exist()


# ── Playwright Browser Configuration ────────────────────────────────────────
@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any],
) -> dict[str, Any]:
    """Configure browser context defaults: viewport, locale, and timezone."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "en-GB",
        "timezone_id": "Europe/London",
    }


# ── Shared Fixtures ──────────────────────────────────────────────────────────
@pytest.fixture
def user_password(request: pytest.FixtureRequest) -> str:
    """Retrieve user password from --user-pw CLI option or USER_PASSWORD env var."""
    password: str = request.config.getoption("--user-pw")
    return password


@pytest.fixture
def app_url(request: pytest.FixtureRequest) -> str:
    """Resolve the base URL for the current test based on its app marker.

    Falls back to --base-url if no app marker is present.
    """
    for app in AppUrl:
        if request.node.get_closest_marker(app.name.lower()):
            return app.value

    base: str | None = request.config.getoption("--base-url", default=None)
    if base:
        return base

    pytest.fail(
        "No app marker (@pytest.mark.saucedemo, @pytest.mark.theinternet, "
        "@pytest.mark.uiplayground) or --base-url provided."
    )


# ── Failure Artifact Capture ─────────────────────────────────────────────────
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],  # noqa: ARG001
) -> Generator[None, pytest.TestReport, None]:
    """Capture screenshot and trace on test failure, attach to Allure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        funcargs: dict[str, Any] = getattr(item, "funcargs", {})
        page: Page | None = funcargs.get("page")
        if page and not page.is_closed():
            _capture_and_attach_screenshot(page, item)
            _capture_and_attach_trace(page, item)


def _capture_and_attach_screenshot(page: Page, item: pytest.Item) -> None:
    """Save a failure screenshot and attach it to the Allure report."""
    test_name = get_last_element(sanitize_nodeid(item.nodeid))
    screenshot_path = SCREENSHOTS_DIR / f"{test_name}.png"

    try:
        page.screenshot(path=str(screenshot_path))
        allure.attach.file(
            str(screenshot_path),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        logger.info("Screenshot saved: %s", screenshot_path)
    except Exception:
        logger.warning(
            "Failed to capture screenshot for %s", item.nodeid, exc_info=True
        )


def _capture_and_attach_trace(page: Page, item: pytest.Item) -> None:
    """Save a Playwright trace and attach it to the Allure report."""
    test_name = get_last_element(sanitize_nodeid(item.nodeid))
    trace_path = TRACES_DIR / f"{test_name}.zip"

    try:
        context = page.context
        context.tracing.stop(path=str(trace_path))
        allure.attach.file(
            str(trace_path),
            name="failure-trace",
            attachment_type=allure.attachment_type.TEXT,
        )
        logger.info("Trace saved: %s", trace_path)
    except Exception:
        logger.warning("Failed to capture trace for %s", item.nodeid, exc_info=True)


# ── Per-Test Logging ─────────────────────────────────────────────────────────
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """Attach a per-test FileHandler to the root logger before the test runs.

    Captures all logging output (test code, page objects, utilities) into
    an individual log file. In xdist parallel mode the filename is prefixed
    with the worker ID to prevent collisions.
    """
    test_name = get_last_element(sanitize_nodeid(item.nodeid))
    log_filename = build_log_filename(test_name)
    log_file = LOG_DIR / log_filename

    handler = logging.FileHandler(str(log_file))
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Store references immediately so teardown can always clean up,
    # even if the remaining setup code raises.
    item._log_handler = handler  # type: ignore[attr-defined]
    item._log_file = log_file  # type: ignore[attr-defined]

    if root_logger.level == logging.NOTSET or root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)

    test_logger = logging.getLogger(item.nodeid)
    test_logger.setLevel(logging.INFO)
    test_logger.info("Starting test - %s", item.nodeid)

    item._test_logger = test_logger  # type: ignore[attr-defined]


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:  # noqa: ARG001
    """Close and remove the per-test FileHandler from the root logger."""
    test_logger: logging.Logger | None = getattr(item, "_test_logger", None)
    handler: logging.FileHandler | None = getattr(item, "_log_handler", None)

    if handler:
        if test_logger:
            test_logger.info("Finished test - %s", item.nodeid)
        handler.close()
        logging.getLogger().removeHandler(handler)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Move the log file of a failed test into the failed_tests/ subdirectory."""
    if report.when == "call" and report.failed:
        test_name = get_last_element(sanitize_nodeid(report.nodeid))
        log_filename = build_log_filename(test_name)
        log_file = LOG_DIR / log_filename
        failed_log_file = FAILED_LOG_DIR / log_filename
        if log_file.exists():
            log_file.rename(failed_log_file)
