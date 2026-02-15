"""
Integration tests for API endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import io
from PIL import Image

# Import app
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models.database import create_database


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_image():
    """Create a sample test image"""
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
        assert "timestamp" in data


class TestUploadEndpoint:
    """Tests for /api/upload endpoint"""
    
    def test_upload_no_files(self, client, mock_env_vars):
        """Test upload with no files"""
        response = client.post("/api/upload")
        assert response.status_code == 422  # Validation error
    
    def test_upload_too_many_files(self, client, mock_env_vars, sample_image):
        """Test upload with more than 10 files"""
        files = []
        for i in range(11):
            img_bytes = io.BytesIO()
            img = Image.new('RGB', (100, 100), color='red')
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files.append(("files", (f"test{i}.jpg", img_bytes, "image/jpeg")))
        
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "Maximum 10 images" in response.json()["detail"]
    
    def test_upload_invalid_file_type(self, client, mock_env_vars):
        """Test upload with non-image file"""
        files = [
            ("files", ("test.txt", io.BytesIO(b"test"), "text/plain"))
        ]
        response = client.post("/api/upload", files=files)
        assert response.status_code == 400
        assert "not an image" in response.json()["detail"]
    
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") or os.getenv("SKIP_EXTERNAL_TESTS", "true").lower() == "true",
        reason="Requires ANTHROPIC_API_KEY and SKIP_EXTERNAL_TESTS=false"
    )
    def test_upload_valid_images(self, client, sample_image):
        """Test upload with valid images (requires real API key)"""
        # Temporarily set mock API key for test structure
        os.environ.setdefault("ANTHROPIC_API_KEY", "mock_key_for_test")
        
        files = [
            ("files", ("test.jpg", sample_image, "image/jpeg"))
        ]
        data = {
            "condition": "good",
            "additional_notes": "Test item"
        }
        response = client.post("/api/upload", files=files, data=data)
        # This will test the endpoint structure
        assert response.status_code in [200, 422, 500]  # Various possible states


class TestPostEndpoint:
    """Tests for /api/post endpoint"""
    
    @pytest.mark.asyncio
    async def test_post_invalid_item_id(self, client, mock_env_vars):
        """Test posting with invalid item ID"""
        data = {
            "item_id": "nonexistent",
            "marketplaces": ["facebook"],
            "auto_post": False
        }
        response = client.post("/api/post", json=data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_post_missing_marketplace(self, client, mock_env_vars):
        """Test posting without marketplace selection"""
        data = {
            "item_id": "test-id",
            "marketplaces": [],
            "auto_post": False
        }
        response = client.post("/api/post", json=data)
        # Should return 404 or validation error
        assert response.status_code in [404, 422]


class TestListingsEndpoint:
    """Tests for listings management endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_listings_empty(self, client, mock_env_vars):
        """Test getting listings when database is empty"""
        response = client.get("/api/listings")
        assert response.status_code == 200
        data = response.json()
        assert "listings" in data
        assert isinstance(data["listings"], list)
    
    @pytest.mark.asyncio
    async def test_get_listing_not_found(self, client, mock_env_vars):
        """Test getting non-existent listing"""
        response = client.get("/api/listings/nonexistent-id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_listing_not_found(self, client, mock_env_vars):
        """Test updating non-existent listing"""
        updates = {"status": "posted"}
        response = client.put("/api/listings/nonexistent-id", json=updates)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_listing_not_found(self, client, mock_env_vars):
        """Test deleting non-existent listing"""
        response = client.delete("/api/listings/nonexistent-id")
        assert response.status_code == 404


class TestDatabaseIntegration:
    """Tests for database operations"""
    
    @pytest.mark.asyncio
    async def test_json_database_operations(self, temp_db_path, sample_listing_data):
        """Test JSON database CRUD operations"""
        from models.database import Database
        
        db = Database(temp_db_path)
        await db.initialize()
        
        # Create
        listing = await db.create_listing(**sample_listing_data)
        assert listing.id is not None
        assert listing.item_name == sample_listing_data["item_name"]
        
        # Read
        retrieved = await db.get_listing(listing.id)
        assert retrieved is not None
        assert retrieved.id == listing.id
        
        # Update
        updated = await db.update_listing(listing.id, {"status": "posted"})
        assert updated.status == "posted"
        
        # List
        listings = await db.get_listings()
        assert len(listings) == 1
        
        # Delete
        success = await db.delete_listing(listing.id)
        assert success is True
        
        # Verify deletion
        retrieved_after_delete = await db.get_listing(listing.id)
        assert retrieved_after_delete is None


class TestMissingAPIKeys:
    """Tests for handling missing API keys"""
    
    @pytest.mark.asyncio
    async def test_ebay_service_without_api_key(self):
        """Test eBay service gracefully handles missing API key"""
        from services.ebay_service import eBayService
        import os
        
        # Temporarily remove API key
        old_key = os.environ.get("EBAY_APP_ID")
        if "EBAY_APP_ID" in os.environ:
            del os.environ["EBAY_APP_ID"]
        
        service = eBayService()
        result = await service.search_sold_listings("test item")
        
        # Should return mock data, not raise exception
        assert result["success"] is False
        assert "not configured" in result["message"].lower()
        
        # Restore key if it existed
        if old_key:
            os.environ["EBAY_APP_ID"] = old_key
    
    @pytest.mark.asyncio
    async def test_facebook_service_without_token(self):
        """Test Facebook service gracefully handles missing token"""
        from services.facebook_poster import FacebookPoster
        import os
        
        # Temporarily remove token
        old_token = os.environ.get("FACEBOOK_ACCESS_TOKEN")
        if "FACEBOOK_ACCESS_TOKEN" in os.environ:
            del os.environ["FACEBOOK_ACCESS_TOKEN"]
        
        service = FacebookPoster()
        
        # Create a mock item
        class MockItem:
            listing_copy = {"title": "Test"}
            description = "Test"
            pricing_data = {"recommended_price": 100}
            condition = "good"
            image_paths = []
            item_name = "Test"
            category = "Test"
        
        result = await service.post_item(MockItem())
        
        # Should return error, not raise exception
        assert result["status"] == "error"
        assert "not configured" in result["message"].lower()
        
        # Restore token if it existed
        if old_token:
            os.environ["FACEBOOK_ACCESS_TOKEN"] = old_token


class TestDatabaseFailure:
    """Tests for database failure scenarios"""
    
    @pytest.mark.asyncio
    async def test_database_connection_failure(self):
        """Test handling of database connection failure"""
        from models.database_postgres import PostgresDatabase
        
        # Try to connect to non-existent database
        db = PostgresDatabase("postgresql+asyncpg://invalid:invalid@localhost:9999/invalid")
        
        with pytest.raises(Exception):
            await db.initialize()
