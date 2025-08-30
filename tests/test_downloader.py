"""
Unit Tests for Video Downloader

This module contains unit tests for the video downloader components.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from src.downloader import VideoDownloader
from src.platform_detector import PlatformDetector
from src.models import DownloadType, DownloadRequest


class TestPlatformDetector:
    """Test cases for PlatformDetector."""
    
    def test_detect_youtube(self):
        """Test YouTube URL detection."""
        urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        for url in urls:
            assert PlatformDetector.detect_platform(url) == "YouTube"
    
    def test_detect_facebook(self):
        """Test Facebook URL detection."""
        urls = [
            "https://www.facebook.com/watch/?v=123456789",
            "https://fb.watch/123456789"
        ]
        
        for url in urls:
            assert PlatformDetector.detect_platform(url) == "Facebook"
    
    def test_detect_twitter(self):
        """Test Twitter/X URL detection."""
        urls = [
            "https://twitter.com/user/status/123456789",
            "https://x.com/user/status/123456789"
        ]
        
        for url in urls:
            assert PlatformDetector.detect_platform(url) == "Twitter/X"
    
    def test_detect_instagram(self):
        """Test Instagram URL detection."""
        urls = [
            "https://www.instagram.com/p/ABC123/",
            "https://instagram.com/reel/XYZ789/"
        ]
        
        for url in urls:
            assert PlatformDetector.detect_platform(url) == "Instagram"
    
    def test_unsupported_platform(self):
        """Test unsupported platform detection."""
        urls = [
            "https://example.com/video",
            "https://unknown-platform.com/video/123"
        ]
        
        for url in urls:
            assert PlatformDetector.detect_platform(url) is None
    
    def test_is_supported_platform(self):
        """Test platform support checking."""
        assert PlatformDetector.is_supported_platform("https://www.youtube.com/watch?v=123")
        assert not PlatformDetector.is_supported_platform("https://example.com/video")
    
    def test_get_supported_platforms(self):
        """Test getting list of supported platforms."""
        platforms = PlatformDetector.get_supported_platforms()
        assert isinstance(platforms, list)
        assert "YouTube" in platforms
        assert "Facebook" in platforms


class TestDownloadRequest:
    """Test cases for DownloadRequest model."""
    
    def test_valid_request(self):
        """Test valid download request."""
        request = DownloadRequest(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            download_type=DownloadType.VIDEO
        )
        assert str(request.url) == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert request.download_type == DownloadType.VIDEO
    
    def test_invalid_platform(self):
        """Test invalid platform URL."""
        with pytest.raises(ValueError):
            DownloadRequest(
                url="https://example.com/video",
                download_type=DownloadType.VIDEO
            )


class TestVideoDownloader:
    """Test cases for VideoDownloader."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = VideoDownloader(download_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Test VideoDownloader initialization."""
        assert self.downloader.download_dir == Path(self.temp_dir)
        assert self.downloader.download_dir.exists()
    
    def test_get_download_options_video(self):
        """Test video download options."""
        options = self.downloader._get_download_options(DownloadType.VIDEO)
        assert 'format' in options
        assert 'merge_output_format' in options
        assert options['merge_output_format'] == 'mp4'
    
    def test_get_download_options_audio(self):
        """Test audio download options."""
        options = self.downloader._get_download_options(DownloadType.AUDIO)
        assert options['extractaudio'] is True
        assert options['audioformat'] == 'mp3'
    
    def test_format_duration(self):
        """Test duration formatting."""
        assert self.downloader._format_duration(None) is None
        assert self.downloader._format_duration(65) == "01:05"
        assert self.downloader._format_duration(3665) == "01:01:05"
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert self.downloader._format_file_size(None) is None
        assert self.downloader._format_file_size(1024) == "1.0 KB"
        assert self.downloader._format_file_size(1048576) == "1.0 MB"
    
    @patch('src.downloader.yt_dlp.YoutubeDL')
    def test_extract_info_success(self, mock_youtubedl):
        """Test successful info extraction."""
        mock_instance = Mock()
        mock_instance.extract_info.return_value = {
            'title': 'Test Video',
            'duration': 120,
            'uploader': 'Test User'
        }
        mock_youtubedl.return_value.__enter__.return_value = mock_instance
        
        info = self.downloader._extract_info("https://www.youtube.com/watch?v=test")
        assert info is not None
        assert info['title'] == 'Test Video'
    
    @patch('src.downloader.yt_dlp.YoutubeDL')
    def test_extract_info_failure(self, mock_youtubedl):
        """Test failed info extraction."""
        mock_instance = Mock()
        mock_instance.extract_info.side_effect = Exception("Network error")
        mock_youtubedl.return_value.__enter__.return_value = mock_instance
        
        info = self.downloader._extract_info("https://www.youtube.com/watch?v=test")
        assert info is None
    
    def test_download_invalid_type(self):
        """Test download with invalid type."""
        result = self.downloader.download(
            "https://www.youtube.com/watch?v=test", 
            "invalid_type"
        )
        assert result['status'] == 'error'
        assert 'Invalid download type' in result['message']
    
    def test_download_unsupported_platform(self):
        """Test download from unsupported platform."""
        result = self.downloader.download(
            "https://example.com/video", 
            "video"
        )
        assert result['status'] == 'error'
        assert 'Unsupported platform' in result['message']
    
    @patch('src.downloader.VideoDownloader._extract_info')
    def test_download_info_extraction_failure(self, mock_extract):
        """Test download when info extraction fails."""
        mock_extract.return_value = None
        
        result = self.downloader.download(
            "https://www.youtube.com/watch?v=test", 
            "video"
        )
        assert result['status'] == 'error'
        assert 'Failed to extract video information' in result['message']


@pytest.fixture
def sample_video_info():
    """Sample video information for testing."""
    return {
        'title': 'Sample Video',
        'duration': 180,
        'uploader': 'Sample User',
        'view_count': 1000,
        'upload_date': '20240101',
        'description': 'This is a sample video description for testing purposes.'
    }


def test_sample_video_info_fixture(sample_video_info):
    """Test the sample video info fixture."""
    assert sample_video_info['title'] == 'Sample Video'
    assert sample_video_info['duration'] == 180
    assert isinstance(sample_video_info['view_count'], int)


if __name__ == "__main__":
    pytest.main([__file__])
