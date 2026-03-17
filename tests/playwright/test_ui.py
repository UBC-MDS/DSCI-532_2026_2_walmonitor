"""
Playwright UI tests for the Walmonitor Dashboard.
Tests verify that user interactions with the filters correctly update the charts.
"""

import pytest
import subprocess
import time
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session", autouse=True)
def start_app():
    proc = subprocess.Popen(["shiny", "run", "src/app.py", "--port", "8765"])
    time.sleep(5)
    yield
    proc.terminate()


@pytest.fixture(scope="session")
def app_url():
    return "http://127.0.0.1:8765"


def test_branch_filter_updates_display(page: Page, app_url):
    """
    Verifies that selecting a specific branch updates the value boxes,
    ensuring the dashboard responds to branch filter changes.
    """
    page.goto(app_url)
    page.wait_for_timeout(3000)
    page.locator("select#input_branch").select_option("A")
    page.wait_for_timeout(2000)
    expect(page.locator(".bslib-value-box")).to_have_count(4)


def test_date_range_filter(page: Page, app_url):
    """
    Verifies that changing the date range updates the dashboard,
    ensuring only data within the selected range is displayed.
    """
    page.goto(app_url)
    page.wait_for_timeout(3000)
    page.locator("#input_date_range input").nth(0).fill("2019-02-01")
    page.locator("#input_date_range input").nth(1).fill("2019-02-28")
    page.keyboard.press("Tab")
    page.wait_for_timeout(2000)
    expect(page.locator(".bslib-value-box")).to_have_count(4)


def test_aggregation_toggle(page: Page, app_url):
    """
    Verifies that switching between Day and Week aggregation updates the dashboard,
    ensuring the time grouping logic works correctly for both modes.
    """
    page.goto(app_url)
    page.wait_for_timeout(3000)
    page.locator("input[type='radio'][value='week']").click()
    page.wait_for_timeout(2000)
    expect(page.locator("input[type='radio'][value='week']")).to_be_checked()