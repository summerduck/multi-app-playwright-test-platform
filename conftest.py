"""
Pytest configuration file for Playwright tests with fixture definitions.

This file contains the configuration for the Pytest framework, including
fixture definitions for page objects, custom arguments, and logging setup. It provides
a consistent environment for running tests with Playwright.
"""

import logging
import os
import re
import shutil
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Base directory for test logs
LOG_DIR = Path("test-logs")
FAILED_LOG_DIR = LOG_DIR / "failed_tests"
SCREENSHOTS_DIR = LOG_DIR / "screenshots"

# Initialize logger
logger = logging.getLogger(__name__)


# Pytest custom add option arguments
def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Pytest custom add option arguments

    This function adds a custom option argument to the Pytest framework.
    It allows for the specification of a user password, which is used
    to authenticate with the application.

    Args:
        parser: The Pytest parser object

    Returns:
        None
    """
    parser.addoption(
        "--user-pw",
        action="store",
        help="USER_PASSWORD",
        default=os.getenv("USER_PASSWORD"),
    )


def make_dir_for_logs() -> None:
    """
    Create directory for logs. Delete exists
    directory if it exists.

    Returns:
        None
    """
    # Check if the directory exists before attempting to delete it
    if LOG_DIR.exists():
        # Delete the directory and its contents
        shutil.rmtree(LOG_DIR)

    # Create a new log directory
    LOG_DIR.mkdir(exist_ok=True)
    FAILED_LOG_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_configure(config: pytest.Config) -> None:
    """
    Pytest configuration setup

    This function sets up the Pytest configuration for the test suite.
    It creates a directory for logs and ensures that the necessary directories
    exist before running the tests.

    In parallel mode (pytest-xdist), only the master process cleans and
    creates log directories. Worker processes just ensure directories exist
    to avoid race conditions.

    Args:
        config: The Pytest configuration object

    Returns:
        None
    """
    load_dotenv()

    if not hasattr(config, "workerinput"):
        # Master process or non-xdist run: safe to clean and recreate
        make_dir_for_logs()
    else:
        # Worker process: just ensure directories exist (no rmtree)
        LOG_DIR.mkdir(exist_ok=True)
        FAILED_LOG_DIR.mkdir(parents=True, exist_ok=True)
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def user_password(request: pytest.FixtureRequest) -> str:
    """
    Fixture to get the user password from the command line.

    This fixture retrieves the user password from the command line.
    It is used to authenticate with the application.

    Args:
        request: The Pytest request object

    Returns:
        str: The user password from the command line
    """
    password: str = request.config.getoption("--user-pw")
    return password


def sanitize_nodeid(node_id: str) -> str:
    """
    Cleans up and formats the test's nodeid
    (a unique identifier for each test in Pytest).
    """
    tokens = node_id.split("::")
    tokens[-1] = tokens[-1].replace("/", "-")
    tokens[-1] = re.sub(r"-+", "-", tokens[-1])
    node_id = "/".join([x for x in tokens if x != "()"])
    return re.sub(r"\[(.+)\]", r"-\1", node_id)


def get_last_element(node_id: str) -> str:
    """
    Retrieves the last part of the sanitized nodeid,
    which represents the specific test name.

    Args:
        node_id: The sanitized nodeid

    Returns:
        str: The last part of the sanitized nodeid
    """
    return node_id.rsplit("/", maxsplit=1)[-1]


def _build_log_filename(test_name: str) -> str:
    """
    Build a log filename with optional xdist worker ID prefix.

    In parallel mode (pytest-xdist), each worker gets a unique ID
    (gw0, gw1, ...) that is prepended to the filename to prevent
    collisions between workers running tests with similar names.

    Args:
        test_name: The sanitized test name

    Returns:
        str: The log filename with optional worker prefix
    """
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "")
    prefix = f"{worker_id}_" if worker_id else ""
    max_filename_length = 255  # NAME_MAX on macOS/Linux (filename only, not path)
    max_name_length = max_filename_length - len(prefix) - len(".log")
    truncated_test_name = test_name[:max_name_length]
    return f"{prefix}{truncated_test_name}.log"


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Configures a per-test file handler before the test runs.

    Attaches a ``FileHandler`` to the **root** logger so that every
    ``logging.getLogger(__name__)`` call in test code, page objects, and
    utilities is captured. Unlike the previous implementation, existing
    handlers from other plugins are **not** cleared -- only our handler
    is added and later removed in teardown.

    In parallel mode the log filename is prefixed with the xdist worker
    ID to prevent file collisions between workers.

    Args:
        item: The Pytest item object

    Returns:
        None
    """
    # Get test node ID for log naming
    test_name = get_last_element(sanitize_nodeid(item.nodeid))
    log_filename = _build_log_filename(test_name)
    log_file = LOG_DIR / log_filename

    # Create a file handler for this test and attach it to the root logger
    # so all loggers (test code, page objects, utilities) are captured.
    handler = logging.FileHandler(str(log_file))
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)

    # Store references on the item immediately after attaching the handler
    # so that teardown can always locate and clean it up, even if the
    # remaining setup code raises an exception.
    item._log_handler = handler  # type: ignore[attr-defined]
    item._log_file = log_file  # type: ignore[attr-defined]

    if root_logger.level == logging.NOTSET or root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)

    # Use a named logger for framework lifecycle messages
    test_logger = logging.getLogger(item.nodeid)
    test_logger.setLevel(logging.INFO)
    test_logger.info("Starting test - %s", item.nodeid)

    item._test_logger = test_logger  # type: ignore[attr-defined]


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """
    Cleans up the per-test file handler after the test is completed.

    Writes a final lifecycle message, then closes and removes the
    handler from the **root** logger. Other plugins' handlers remain
    untouched.

    Args:
        item: The Pytest item object
        nextitem: The next Pytest item object

    Returns:
        None
    """
    test_logger: logging.Logger | None = getattr(item, "_test_logger", None)
    handler: logging.FileHandler | None = getattr(item, "_log_handler", None)

    if handler:
        if test_logger:
            test_logger.info("Finished test - %s", item.nodeid)
        handler.close()
        # Remove our handler from the root logger (not the named one)
        logging.getLogger().removeHandler(handler)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """
    Handles special processing for logs of failed tests.

    Moves the log file of a failed test into the ``failed_tests/``
    subdirectory. Uses the same worker-ID-prefixed filename that was
    built during setup to locate the correct log file.

    Args:
        report: The Pytest report object

    Returns:
        None
    """
    if report.when == "call" and report.failed:
        test_name = get_last_element(sanitize_nodeid(report.nodeid))
        log_filename = _build_log_filename(test_name)
        log_file = LOG_DIR / log_filename
        failed_log_file = FAILED_LOG_DIR / log_filename
        if log_file.exists():
            log_file.rename(failed_log_file)
