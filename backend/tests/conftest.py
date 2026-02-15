"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
import os
from pathlib import Path
import tempfile
import shutil


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for file storage during tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path"""
    db_path = tmp_path / "test_listings.json"
    return str(db_path)


@pytest.fixture
def mock_env_vars(monkeypatch, temp_storage_dir):
    """Set up mock environment variables for testing"""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key")
    monkeypatch.setenv("UPLOAD_DIR", temp_storage_dir)
    monkeypatch.delenv("EBAY_APP_ID", raising=False)
    monkeypatch.delenv("FACEBOOK_ACCESS_TOKEN", raising=False)


@pytest.fixture
def sample_listing_data():
    """Sample listing data for tests"""
    return {
        "item_name": "Test Item",
        "category": "Electronics",
        "brand": "TestBrand",
        "condition": "good",
        "description": "A test item description",
        "image_paths": ["/path/to/image1.jpg"],
        "pricing_data": {
            "recommended_price": 100.00,
            "quick_sale_price": 85.00
        },
        "marketplace_recommendations": [
            {"platform": "facebook", "match_score": 0.95}
        ],
        "listing_copy": {
            "title": "Test Item - Great Condition",
            "description": "Full description here"
        }
    }
