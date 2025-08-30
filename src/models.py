"""
Video Downloader Models

This module contains Pydantic models for request/response validation.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, validator


class DownloadType(str, Enum):
    """Enumeration for supported download types."""
    VIDEO = "video"
    AUDIO = "audio"


class DownloadRequest(BaseModel):
    """Model for download request validation."""
    url: HttpUrl
    download_type: DownloadType
    
    @validator('url')
    def validate_url(cls, v):
        """Validate that the URL is from a supported platform."""
        url_str = str(v)
        supported_domains = [
            'youtube.com', 'youtu.be', 'facebook.com', 'fb.watch',
            'twitter.com', 'x.com', 'instagram.com', 'tiktok.com',
            'vimeo.com', 'dailymotion.com', 'twitch.tv'
        ]
        
        if not any(domain in url_str for domain in supported_domains):
            raise ValueError(f"URL must be from a supported platform: {', '.join(supported_domains)}")
        
        return v


class DownloadResponse(BaseModel):
    """Model for download response."""
    status: str
    message: str
    file_path: Optional[str] = None
    platform: Optional[str] = None
    download_type: Optional[str] = None
    file_size: Optional[str] = None
    duration: Optional[str] = None


class ErrorResponse(BaseModel):
    """Model for error responses."""
    status: str = "error"
    message: str
    file_path: Optional[str] = None
    platform: Optional[str] = None
    download_type: Optional[str] = None
