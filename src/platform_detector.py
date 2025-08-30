"""
Platform Detection Utilities

This module contains utilities for detecting and validating video platforms.
"""

import re
from typing import Optional


class PlatformDetector:
    """Utility class for detecting video platforms from URLs."""
    
    PLATFORM_PATTERNS = {
        'YouTube': [
            r'(?:youtube\.com|youtu\.be)',
            r'youtube\.com/watch\?v=',
            r'youtu\.be/',
            r'youtube\.com/embed/',
            r'youtube\.com/v/'
        ],
        'Facebook': [
            r'facebook\.com',
            r'fb\.watch',
            r'facebook\.com/watch',
            r'facebook\.com/.*?/videos'
        ],
        'Twitter/X': [
            r'twitter\.com',
            r'x\.com',
            r'twitter\.com/.*?/status',
            r'x\.com/.*?/status'
        ],
        'Instagram': [
            r'instagram\.com',
            r'instagram\.com/p/',
            r'instagram\.com/reel/',
            r'instagram\.com/tv/'
        ],
        'TikTok': [
            r'tiktok\.com',
            r'tiktok\.com/@.*?/video'
        ],
        'Vimeo': [
            r'vimeo\.com',
            r'vimeo\.com/\d+'
        ],
        'Twitch': [
            r'twitch\.tv',
            r'twitch\.tv/videos',
            r'twitch\.tv/.*?/clip'
        ],
        'Dailymotion': [
            r'dailymotion\.com',
            r'dailymotion\.com/video'
        ]
    }
    
    @classmethod
    def detect_platform(cls, url: str) -> Optional[str]:
        """
        Detect the platform from a given URL.
        
        Args:
            url (str): The video URL to analyze
            
        Returns:
            Optional[str]: The detected platform name or None if not supported
        """
        url = url.lower()
        
        for platform, patterns in cls.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url):
                    return platform
        
        return None
    
    @classmethod
    def is_supported_platform(cls, url: str) -> bool:
        """
        Check if the URL is from a supported platform.
        
        Args:
            url (str): The video URL to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        return cls.detect_platform(url) is not None
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        Get a list of all supported platforms.
        
        Returns:
            list: List of supported platform names
        """
        return list(cls.PLATFORM_PATTERNS.keys())
