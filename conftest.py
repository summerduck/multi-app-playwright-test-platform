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
import sys
from dotenv import load_dotenv

import pytest
import allure
from playwright.sync_api import Page

# Handle display of output log when using xdist
sys.stdout = sys.stderr

# Base directory for test logs
LOG_DIR = "test-logs"
FAILED_LOG_DIR = os.path.join(LOG_DIR, "failed_tests")
SCREENSHOTS_DIR = os.path.join(LOG_DIR, "screenshots")

# Initialize logger
logger = logging.getLogger(__name__)


@pytest.fixture()
def customer_account_create_page(page: Page) -> CustomerAccountCreatePage:
    """
    Fixture to initialize the CustomerAccountCreatePage instance.

    This fixture creates an instance of the CustomerAccountCreatePage class,
    which is a page object for the customer account creation page. It provides
    a consistent environment for running tests with Playwright.

    Args:
        page (Page): Playwright Page instance for browser interactions

    Returns:
        CustomerAccountCreatePage: Instance of the CustomerAccountCreatePage class
    """
    return CustomerAccountCreatePage(page)


@pytest.fixture()
def customer_account_page(page: Page) -> CustomerAccountPage:
    """Fixture to initialize the CustomerAccountPage instance.

    This fixture creates an instance of the CustomerAccountPage class,
    which is a page object for the customer account page. It provides
    a consistent environment for running tests with Playwright.

    Args:
        page (Page): Playwright Page instance for browser interactions

    Returns:
        CustomerAccountPage: Instance of the CustomerAccountPage class
    """
    return CustomerAccountPage(page)


@pytest.fixture()
def eco_friendly_page(page: Page) -> EcoFriendlyPage:
    """Fixture to initialize the EcoFriendlyPage instance.

    This fixture creates an instance of the EcoFriendlyPage class,
    which is a page object for the eco-friendly page. It provides
    a consistent environment for running tests with Playwright.

    Args:
        page (Page): Playwright Page instance for browser interactions

    Returns:
        EcoFriendlyPage: Instance of the EcoFriendlyPage class
    """
    return EcoFriendlyPage(page)


@pytest.fixture()
def sale_page(page: Page) -> SalePage:
    """Fixture to initialize the SalePage instance.

    This fixture creates an instance of the SalePage class,
    which is a page object for the sale page. It provides
    a consistent environment for running tests with Playwright.

    Args:
        page (Page): Playwright Page instance for browser interactions

    Returns:
        SalePage: Instance of the SalePage class
    """
    return SalePage(page)


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
    # Load the .env file
    load_dotenv()
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
    if os.path.exists(LOG_DIR):
        # Delete the directory and its contents
        shutil.rmtree(LOG_DIR)

    # Create a new log directory
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(FAILED_LOG_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


def pytest_configure(config: pytest.Config) -> None:
    """
    Pytest configuration setup

    This function sets up the Pytest configuration for the test suite.
    It creates a directory for logs and ensures that the necessary directories
    exist before running the tests.

    Args:
        config: The Pytest configuration object

    Returns:
        None
    """
    make_dir_for_logs()


@pytest.fixture
def user_password(request) -> str:
    """
    Fixture to get the user password from the command line.

    This fixture retrieves the user password from the command line.
    It is used to authenticate with the application.

    Args:
        request: The Pytest request object

    Returns:
        str: The user password from the command line
    """
    return request.config.getoption("--user-pw")


def sanitize_nodeid(node_id: str) -> str:
    """
    Cleans up and formats the test's nodeid
    (a unique identifier for each test in Pytest).
    """
    tokens = node_id.split("::")
    tokens[-1] = tokens[-1].replace("/", "-")
    tokens[-1] = re.sub(r"-+", "-", tokens[-1])
    node_id = "/".join([x for x in tokens if x != "()"])
    node_id = re.sub(r"\[(.+)\]", r"-\1", node_id)
    return node_id


def get_last_element(node_id: str) -> str:
    """
    Retrieves the last part of the sanitized nodeid,
    which represents the specific test name.

    Args:
        node_id: The sanitized nodeid

    Returns:
        str: The last part of the sanitized nodeid
    """
    return node_id.split("/")[-1]


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item: pytest.Item) -> None:
    """
    Configures a unique logger for each test before it runs

    This function configures a unique logger for each test before it runs.
    It creates a log file for the test and removes any existing handlers.

    Args:
        item: The Pytest item object

    Returns:
        None
    """
    # Get test node ID for log naming
    test_name = get_last_element(sanitize_nodeid(item.nodeid))
    max_filename_length = 255
    truncated_test_name = test_name[
        : max_filename_length - len(LOG_DIR) - 5
    ]  # 5 for ".log" and separators
    log_file = os.path.join(LOG_DIR, f"{truncated_test_name}.log")

    # Configure logging for the current test
    logger = logging.getLogger()
    logger.handlers = []  # Remove any existing handlers
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.info("Starting test - %s", item.nodeid)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item) -> None:
    """
    Cleans up the logger after the test is completed

    This function cleans up the logger after the test is completed.
    It removes the test-specific handlers and closes the log file.

    Args:
        item: The Pytest item object
        nextitem: The next Pytest item object

    Returns:
        None
    """
    logger = logging.getLogger()
    logger.info("Finished test - %s", item.nodeid)

    # Remove test-specific handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logger.removeHandler(handler)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """
    Handles special processing for logs of failed tests

    This function handles special processing for logs of failed tests.
    It renames the log file to a failed log file if the test fails.

    Args:
        report: The Pytest report object

    Returns:
        None
    """
    if report.when == "call" and report.failed:
        test_name = get_last_element(sanitize_nodeid(report.nodeid))
        log_file = os.path.join(LOG_DIR, f"{test_name}.log")
        failed_log_file = os.path.join(FAILED_LOG_DIR, f"{test_name}.log")
        if os.path.exists(log_file):
            os.rename(log_file, failed_log_file)


# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """
#     Capture screenshots on test failures and attach them to Allure reports.
#     """
#     outcome = yield
#     report = outcome.get_result()

#     # Capture screenshot on failure
#     if report.when == "call" and report.failed:
#         try:
#             # Check if page fixture is in use
#             page = item.funcargs.get("page", None)
#             if page:
#                 # Create screenshots directory if it doesn't exist
#                 os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

#                 # Generate a safe filename
#                 test_name = get_last_element(sanitize_nodeid(item.nodeid))
#                 timestamp = re.sub(r"[^0-9]", "", str(report.longrepr))[:8]
#                 screenshot_name = f"{test_name}_{timestamp}.png"
#                 screenshot_path = os.path.join(SCREENSHOTS_DIR, screenshot_name)

#                 # Take screenshot
#                 page.screenshot(path=screenshot_path)

#                 # Attach screenshot to Allure report
#                 with open(screenshot_path, "rb") as f:
#                     allure.attach(
#                         f.read(),
#                         name=f"Screenshot on failure: {test_name}",
#                         attachment_type=allure.attachment_type.PNG,
#                     )

#                 # Get page source to help with debugging
#                 page_source = page.content()
#                 allure.attach(
#                     page_source,
#                     name="Page Source",
#                     attachment_type=allure.attachment_type.HTML,
#                 )

#         except Exception as e:
#             logger.error("Failed to capture screenshot: %s", str(e))
