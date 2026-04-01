import pytest
from playwright.sync_api import sync_playwright
import time
import random
import string

@pytest.fixture(scope="session")
def browser():
    """
    Launch a browser once for all tests.
    
    scope="session" means this runs ONCE for the entire test session,
    not per-test. Launching a browser is slow, so we reuse it.
    
    headless=False means you can SEE the browser — great for learning!
    Change to headless=True for CI/CD pipelines.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        yield browser
        browser.close()
    

@pytest.fixture
def page(browser):
    """
    Create a fresh browser tab for each test.
    
    Each test gets its own page (tab), so they don't interfere
    with each other. The page is closed after the test.
    """
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def unique_user():
    """
    Generate a unique username for each test.
    
    Why? If you run tests multiple times, "testuser" might already
    exist in the database. Random names avoid this conflict.
    """
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
    return {
        "username": f"username_{random_suffix}",
        "password": "testpass123"
    }

@pytest.fixture
def app_url():
    """
    The URL where the frontend is running.
    """
    return "http://localhost:3000"

@pytest.fixture
def register_and_login(page, app_url, unique_user):
    """
    A helper fixture that registers a user and logs them in.
    
    Many tests need an authenticated user as a starting point.
    This fixture handles the repetitive setup so tests can
    focus on what they're actually testing.
    """
    page.goto(app_url)

    # register
    page.fill("#auth-username", unique_user["username"])
    page.fill("#auth-password", unique_user["password"])
    page.click("button:has-text('Register')")

    # wait for success message
    page.wait_for_selector(".message-success", timeout=5000)

    # now login
    page.fill("#auth-username", unique_user["username"])
    page.fill("#auth-password", unique_user["password"])
    page.click("button:has-text('Login')")

    # wait for main screen to appear
    page.wait_for_selector("#main-screen:not(.hidden)", timeout=5000)

    return unique_user