"""
Tests for the authentication endpoints.

Each test function:
- Starts with 'test_' (pytest discovers them automatically)
- Gets fixtures as parameters (pytest injects them)
- Uses 'assert' to check if things are correct

Naming convention: test_<what>_<expected_result>
Example: test_register_success, test_login_wrong_password
"""

class TestRegister:
    """Groap all registration test together"""

    def test_regisger_success(self, client):
        """A new user should be able to register"""
        response = client.post("/auth/register", json={
            "username": "newuser",
            "password": "newpass123"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["message"] == "User created successfully!"
        assert "id" in data

    def test_register_duplicate_username(self, client):
        """Registering with an existing username should fail"""
        # Register first time
        client.post("/auth/register", json={
            "username": "sameuser",
            "password": "pass123"
        })
        
        # Try register again with same username
        response = client.post("/auth/register", json={
            "username": "sameuser",
            "password": "password"
        })

        assert response.status_code == 400
        assert response.json()["detail"] == "Username already taken"

    def test_register_missing_username(self, client):
        """Registration without username should fail"""
        response = client.post("/auth/register", json={
            "password": "pass123"
        })

        assert response.status_code == 422
    
    def test_register_missing_password(self, client):
        """Registration without password should fail"""
        response = client.post("/auth/register", json={
            "username": "nopassuser"
        })

        assert response.status_code == 422
    
    def test_register_empty_body(self, client):
        """Registration with no data should fail"""
        response = client.post("/auth/register", json={
        })

        assert response.status_code == 422

class TestLogin:
    """Groap all login tests together"""

    def test_login_success(self, client, registered_user):
        """A registrated user should be able to login"""
        response = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def login_wrong_password(self, client, registered_user):
        """Login with wrong password should fail"""
        response = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": "wrongpassword"
        })

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_nonexisting_user(self, client):
        """Login with a username that doesn't exist should fail"""
        response = client.post("/auth/login", data={
            "username": "ghostuser",
            "password": "anypass"
        })
        assert response.status_code == 401

    def test_login_returns_valid_token(self, client, registered_user):
        """The token fromn login should work for authenticated requests"""
        # Login
        login_response = client.post("/auth/login", data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        })
        token = login_response.json()["access_token"]

        # use the token - try accessing a protected endpoint
        # even if it fails for other reason, it shouldn't return 401
        response = client.post(
            "/transcribe",
            headers={"Authorization": f"Bearer {token}"},
            files={"audio": ("test.wav", b"fake audio content", "audio/wav")}
        )
        # should NOT be 401 - the token should be accepted
        assert response.status_code != 401

class TestProtectedAccess:
    """Test that protected endpoints require authentication."""

    def test_transcribe_without_token(self, client):
        """Accessing / transcribe without require authentication"""
        response = client.post(
            "/transcribe",
            files={"audio": ("test.wav", b"fake audio", "audio/wav")}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_transcribe_with_invalid_token(self, client):
        """Using a fake token should return 401."""
        response = client.post(
            "/transcribe",
            headers={"Authorization": "Bearer this-is-fake-token"},
            files={"audio": ("test.wav", b"fake audio", "audio/wav")}
        )
        assert response.status_code == 401
    
    def test_transcribe_with_expired_format_token(self, client):
        """Using a malformed authorization header should return 401"""
        response = client.post(
            "/transcribe",
            headers={"Authorization": "NotBearer sometoken"},
            files={"audio": ("test.wav", b"fake audio", "audio/wav")}
        )
        assert response.status_code == 401