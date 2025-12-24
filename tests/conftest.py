"""
Pytest fixtures for backend API testing.
"""
import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from web_app.main import app
from web_app.db import get_connection

@pytest.fixture
def client():
    """Provide test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
def test_db():
    """Provide in-memory test database"""
    # Use in-memory SQLite for tests
    original_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = ":memory:"
    
    # Initialize database tables
    from web_app.main import init_database
    import asyncio
    asyncio.run(init_database())
    
    conn = get_connection()
    yield conn
    
    conn.close()
    
    # Restore original DB path
    if original_db_path:
        os.environ["DB_PATH"] = original_db_path
    else:
        os.environ.pop("DB_PATH", None)

@pytest.fixture
def mock_user():
    """Provide mock user data for authentication tests"""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com"
    }

@pytest.fixture
def auth_headers(mock_user):
    """
    Provide authentication headers.
    Note: This is a simplified version. In real tests, you'd need to:
    1. Create a test user in Supabase
    2. Get a real JWT token
    3. Use that token in headers
    """
    # For now, we'll test endpoints that don't require auth
    # or mock the authentication
    return {}
