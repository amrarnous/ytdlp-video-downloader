"""
API Tests for Video Downloader

This module contains tests for the FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_downloader():
    """Mock downloader for testing."""
    with patch('src.api.downloader') as mock:
        yield mock


class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "supported_platforms" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_download_success(self, client, mock_downloader):
        """Test successful download."""
        mock_downloader.download.return_value = {
            "status": "success",
            "message": "Video downloaded successfully.",
            "file_path": "/path/to/video.mp4",
            "platform": "YouTube",
            "download_type": "video"
        }
        
        response = client.post(
            "/download",
            json={
                "url": "https://www.youtube.com/watch?v=test",
                "download_type": "video"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["platform"] == "YouTube"
    
    def test_download_invalid_url(self, client):
        """Test download with invalid URL."""
        response = client.post(
            "/download",
            json={
                "url": "https://example.com/video",
                "download_type": "video"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_download_invalid_type(self, client):
        """Test download with invalid type."""
        response = client.post(
            "/download",
            json={
                "url": "https://www.youtube.com/watch?v=test",
                "download_type": "invalid"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_download_error(self, client, mock_downloader):
        """Test download error."""
        mock_downloader.download.return_value = {
            "status": "error",
            "message": "Download failed",
            "file_path": None,
            "platform": "YouTube",
            "download_type": "video"
        }
        
        response = client.post(
            "/download",
            json={
                "url": "https://www.youtube.com/watch?v=test",
                "download_type": "video"
            }
        )
        
        assert response.status_code == 400
    
    def test_info_success(self, client, mock_downloader):
        """Test successful info retrieval."""
        mock_downloader.get_video_info.return_value = {
            "status": "success",
            "message": "Video information extracted successfully.",
            "platform": "YouTube",
            "title": "Test Video",
            "duration": "03:00"
        }
        
        response = client.post(
            "/info",
            json={"url": "https://www.youtube.com/watch?v=test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["title"] == "Test Video"
    
    def test_info_missing_url(self, client):
        """Test info endpoint without URL."""
        response = client.post("/info", json={})
        assert response.status_code == 400
    
    def test_files_list(self, client):
        """Test files listing endpoint."""
        response = client.get("/files")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "count" in data
        assert isinstance(data["files"], list)


if __name__ == "__main__":
    pytest.main([__file__])
