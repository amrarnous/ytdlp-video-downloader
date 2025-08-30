"""
Test Configuration

This module contains test configuration and fixtures.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture(scope="session")
def temp_download_dir():
    """Create a temporary download directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_urls():
    """Sample URLs for testing different platforms."""
    return {
        "youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "youtube_short": "https://youtu.be/dQw4w9WgXcQ",
        "facebook": "https://www.facebook.com/watch/?v=123456789",
        "twitter": "https://twitter.com/user/status/123456789",
        "x": "https://x.com/user/status/123456789",
        "instagram": "https://www.instagram.com/p/ABC123/",
        "tiktok": "https://www.tiktok.com/@user/video/123456789",
        "vimeo": "https://vimeo.com/123456789",
        "unsupported": "https://example.com/video/123"
    }
