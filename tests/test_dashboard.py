"""
Tests for /api/dashboard endpoint - User dashboard data
"""
import pytest
from fastapi.testclient import TestClient

def test_dashboard_requires_auth(client: TestClient):
    """Test that dashboard endpoint requires authentication"""
    response = client.get("/api/dashboard")
    
    # Should require authentication
    assert response.status_code in [401, 403], \
        f"Expected 401/403 for unauthorized access, got {response.status_code}"

@pytest.mark.skip(reason="Requires authentication setup")
def test_dashboard_returns_user_data():
    """Test that dashboard returns correct user data structure"""
    # TODO: Implement when auth is set up
    pass
