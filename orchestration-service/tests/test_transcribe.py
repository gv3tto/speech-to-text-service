"""
Tests for the transcription endpoint.

Since we don't want to load the actual Whisper model in tests
(it's slow and heavy), we test what we CAN test:
- Authentication is enforced
- File validation works
- Correct error handling

The actual transcription is tested via the model service's own tests.
"""
import os

class TestTranscribeValidation:
    """Test input validation for the /transcribe endpoint"""
    
    def test_transcribe_requires_auth(self, client):
        """Should return 401 without validation"""
        response = client.post(
            "/transcribe",
            files={"audio": ("test.wav", b"audio content", "audio/wav")}
        )
        assert response.status_code == 401
    
    def test_transcribe_no_file(self, client, auth_token):
        """Should return 422 when no file is uploaded"""
        response = client.post(
            "/transcribe",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 422


    def test_transcribe_authenticated_user_accepted(self, client, auth_token):
        """An authenticated request with a file should NOT return 401"""
        response = client.post(
            "/transcribe",
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"audio": ("test.wav", b"fake audio data", "audio/wav")}
        )
        assert response.status_code != 401

class TestHealthCheck:
    """Test the health check endpoint"""

    def test_health_check(self, client):
        """Health endpoint should return status healthy"""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "orchestration-service"

    def test_health_check_no_auth_required(self, client):
        """Health endpoint should work without authentication"""
        response = client.get("/health")
        assert response.status_code == 200