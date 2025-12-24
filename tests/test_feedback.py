"""
Tests for /api/feedback endpoint - User feedback system
"""
import pytest
from fastapi.testclient import TestClient

def test_feedback_endpoint_accepts_anonymous(client: TestClient):
    """Test that feedback endpoint accepts anonymous submissions"""
    response = client.post("/api/feedback", json={
        "feedback_type": "bug",
        "content": "Test feedback content",
        "contact": "test@example.com"
    })
    
    # Should succeed (200) or require auth (401/403), NOT crash (500)
    assert response.status_code in [200, 201, 401, 403], \
        f"Expected 200/201/401/403, got {response.status_code}"

def test_feedback_validates_type(client: TestClient):
    """Test that feedback type validation works"""
    response = client.post("/api/feedback", json={
        "feedback_type": "invalid_type",
        "content": "Test content"
    })
    
    # Should return 400 for invalid type
    assert response.status_code == 400

def test_feedback_requires_content(client: TestClient):
    """Test that feedback content is required"""
    response = client.post("/api/feedback", json={
        "feedback_type": "bug",
        "content": ""
    })
    
    # Should return 400 for empty content
    assert response.status_code == 400

def test_feedback_validates_email_format(client: TestClient):
    """Test that email validation works"""
    response = client.post("/api/feedback", json={
        "feedback_type": "feature",
        "content": "Test content",
        "contact": "invalid-email"
    })
    
    # Should return 400 for invalid email
    assert response.status_code == 400

def test_feedback_length_limit(client: TestClient):
    """Test that content length is limited to 500 characters"""
    long_content = "x" * 501
    response = client.post("/api/feedback", json={
        "feedback_type": "bug",
        "content": long_content
    })
    
    # Should return 400 for content too long
    assert response.status_code == 400
