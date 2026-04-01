"""
End-to-End tests for the Speech-to-Text application.

These tests use Playwright to control a real browser and test
the complete user journey — just like a real user would.

IMPORTANT: Both services AND the frontend must be running before
running these tests:
  - Model service on port 8001
  - Orchestration service on port 8000
  - Frontend on port 3000 (or open index.html)

Playwright concepts used:
  - page.goto()          → navigate to a URL
  - page.fill()          → type text into an input
  - page.click()         → click a button/link
  - page.wait_for_selector() → wait for an element to appear
  - page.locator()       → find elements on the page
  - page.is_visible()    → check if something is shown
  - expect()             → make assertions about the page
"""
import os
from playwright.sync_api import expect

class TestPageReload:
    """Test that the page loads correctly"""

    def test_page_title(self, page, app_url):
        """The page should have the correct title."""
        page.goto(app_url)
        expect(page).to_have_title("Speech to Text Service")

    def test_auth_screen_visible_on_load(self, page, app_url):
        """The login form should be visible when the page first loads"""
        page.goto(app_url)

        # auth screen should be visible
        auth_screen = page.locator("#auth-screen")
        expect(auth_screen).to_be_visible()

        # main screen should be hidden
        main_screen = page.locator("#main-screen")
        expect(main_screen).to_be_hidden()

    def test_login_has_inputs(self, page, app_url):
        """The login form should have username and password fields"""
        page.goto(app_url)

        expect(page.locator("#auth-username")).to_be_visible()
        expect(page.locator("#auth-password")).to_be_visible()

    def test_login_and_register_buttons_visible(self, page, app_url):
        page.goto(app_url)

        expect(page.locator("button:has-text('Login')")).to_be_visible()
        expect(page.locator("button:has-text('Register')")).to_be_visible()

class TestRegistration:
    """Test the user registration flow"""

    def test_registration_success(self, page, app_url, unique_user):
        """A new user should see a success message after registering"""
        page.goto(app_url)

        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Register')")

        # wait for and check success message
        success = page.locator(".message-success")
        expect(success).to_be_visible(timeout=5000)
        expect(success).to_contain_text("Account created")

    def test_register_duplicate_shows_error(self, page, app_url, unique_user):
        """Registering the same username twice should show an error"""
        page.goto(app_url)

        # register first time
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Register')")
        page.wait_for_selector(".message-success", timeout=5000)

        # register again with same username
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", "differentpass")
        page.click("button:has-text('Register')")

        # should show error
        error = page.locator(".message-error")
        expect(error).to_be_visible(timeout=5000)
        expect(error).to_contain_text("Please enter")

class TestLogin:
    """Test the login flow"""

    def test_login_success_shows_main_screen(self, page, app_url, unique_user):
        """After successful login, the main screen should appear"""
        page.goto(app_url)

        # register first
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Register')")
        page.wait_for_selector(".message-success", timeout=5000)

        # login
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Login')")

        # main screen should appear
        expect(page.locator("#main-screen")).to_be_vissible(timeout=5000)
        # auth screen should be hidden
        expect(page.locator("#auth-screen")).to_be_hidden
    
    
    def test_login_shows_username_in_header(self, page, app_url, unique_user):
        """After login, the username should appear in the header"""
        page.goto(app_url)

        # register and login
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Register')")
        page.wait_for_selector(".message-success", timeout=5000)

        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Login')")

        # ssername should be in the header
        page.wait_for_selector("#main-screen:not(.hidden)", timeout=5000)
        expect(page.locator("#username-display")).to_contain_text(unique_user["username"])


    def test_login_wrong_password_shows_error(self, page, app_url, unique_user):
        """Login with wrong password should show an error"""
        page.goto(app_url)

        # register
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", unique_user["password"])
        page.click("button:has-text('Register')")
        page.wait_for_selector(".message-success", timeout=5000)

        # login with wrong password
        page.fill("#auth-username", unique_user["username"])
        page.fill("#auth-password", "wrongpassword")
        page.click("button:has-text('Login')")

        error = page.locator(".message-error")
        expect(error).to_be_visible(timeout=5000)

    
    def test_login_empty_fields_shows_error(self, page, app_url):
        """Clicking Login with empty fields should show an error"""
        page.goto(app_url)

        page.click("button:has-text('Login')")

        error = page.locator(".message-error")
        expect(error).to_be_visible(timeout=5000)


class TestLogout:
    """Test the logout flow"""

    def test_logout_returns_to_auth_screen(self, page, app_url, register_and_login):
        """Clicking logout should return to the login screen."""
        # we're already logged with register_and_login fixture

        page.click("button:has-text('Logout')")

        # auth screen should reappear
        expect(page.locator("#auth-screen")).to_be_visible(timeout=5000)
        expect(page.locator("#main-screen")).to_be_hidden()


class TestTranscriptionUI:
    """Test the transcription interface elements"""

    def test_upload_area_visible_after_login(self, page, app_url, register_and_login):
        """The upload area should be visible after login"""
        expect(page.locator("#upload-area")).to_be_visible()

    def test_transcribe_button_disabled_without_file(self, page, app_url, register_and_login):
        """The transcribe button should be disabled when no file is selected"""
        expect(page.locator("#transcribe-btn")).to_be_disabled()

    def test_file_select_enables_button(self, page, app_url, register_and_login):
        """Selecting a file should enable the transcribe button"""
        # create a small test audio file
        test_audio_path = os.path.join(os.path.dirname(__file__), "test_audio.wav")

        # create a minimal WAV file (44 bytes header + silence)
        wav_header = (
            b'RIFF'
            b'\x24\x00\x00\x00'   # File size - 8
            b'WAVE'
            b'fmt '
            b'\x10\x00\x00\x00'   # Chunk size
            b'\x01\x00'           # PCM format
            b'\x01\x00'           # Mono
            b'\x44\xac\x00\x00'   # 44100 Hz
            b'\x88\x58\x01\x00'   # Byte rate
            b'\x02\x00'           # Block align
            b'\x10\x00'           # Bits per sample
            b'data'
            b'\x00\x00\x00\x00'   # Data size
        )

        with open(test_audio_path, "wb") as f:
            f.write(wav_header)

        try:
            # upload the file
            page.locator("#file-input").set_input_files(test_audio_path)

            # button should now be enabled
            expect(page.locator("#transcribe-btn")).to_be_enabled()

            # filename should be displayed
            expect(page.locator("#file-name")).to_be_visible()
        finally:
            # clean up
            if os.path.exists(test_audio_path):
                os.remove(test_audio_path)