"""
Video Downloader Package

A multi-platform video and audio downloader supporting YouTube, Facebook,
Twitter/X, Instagram, TikTok, and other platforms.
"""

from .downloader import VideoDownloader
from .platform_detector import PlatformDetector
from .models import DownloadRequest, DownloadResponse, ErrorResponse, DownloadType

__version__ = "1.0.0"
__author__ = "Video Downloader Team"
__email__ = "contact@example.com"

__all__ = [
    "VideoDownloader",
    "PlatformDetector", 
    "DownloadRequest",
    "DownloadResponse",
    "ErrorResponse",
    "DownloadType"
]
