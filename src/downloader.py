"""
Video Downloader Core Module

This module contains the main VideoDownloader class that handles
video and audio downloading from various platforms using yt-dlp.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp
from .platform_detector import PlatformDetector
from .models import DownloadResponse, ErrorResponse, DownloadType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoDownloader:
    """
    Main class for downloading videos and audio from various platforms.
    
    This class uses yt-dlp to download media from supported platforms
    including YouTube, Facebook, Twitter/X, Instagram, TikTok, and others.
    """
    
    def __init__(self, download_dir: str = "downloads"):
        """
        Initialize the VideoDownloader.
        
        Args:
            download_dir (str): Directory to save downloaded files
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
        # Base yt-dlp options
        self.base_options = {
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'extractaudio': False,
            'format': 'best',
        }
    
    def _get_download_options(self, download_type: DownloadType) -> Dict[str, Any]:
        """
        Get yt-dlp options based on download type.
        
        Args:
            download_type (DownloadType): Type of download (video or audio)
            
        Returns:
            Dict[str, Any]: yt-dlp options dictionary
        """
        options = self.base_options.copy()
        
        if download_type == DownloadType.AUDIO:
            options.update({
                # Use a more robust audio format selection
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': '192K',
                'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                # Ensure we keep trying different extractors
                'ignoreerrors': False,
                'no_warnings': False,
            })
        else:  # video
            options.update({
                # More flexible video format selection with multiple fallbacks
                'format': (
                    'best[height<=1080][ext=mp4]/'
                    'best[height<=720][ext=mp4]/'
                    'best[ext=mp4]/'
                    'best[height<=1080]/'
                    'best[height<=720]/'
                    'worst[height>=360]/'
                    'best'
                ),
                'merge_output_format': 'mp4',
                'writesubtitles': False,
                'writeautomaticsub': False,
            })
        
        return options
    
    def _extract_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract video information without downloading.
        
        Args:
            url (str): Video URL
            
        Returns:
            Optional[Dict[str, Any]]: Video information or None if failed
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"Failed to extract info for {url}: {str(e)}")
            return None
    
    def list_formats(self, url: str) -> Dict[str, Any]:
        """
        List available formats for a video URL.
        
        Args:
            url (str): Video URL
            
        Returns:
            Dict[str, Any]: Available formats or error response
        """
        try:
            # Detect platform
            platform = PlatformDetector.detect_platform(url)
            if not platform:
                return ErrorResponse(
                    message=f"Unsupported platform or invalid URL. Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}"
                ).dict()
            
            # Extract video information including formats
            info = self._extract_info(url)
            if not info:
                return ErrorResponse(
                    message="Failed to extract video information.",
                    platform=platform
                ).dict()
            
            formats = info.get('formats', [])
            available_formats = []
            
            for fmt in formats:
                format_info = {
                    'format_id': fmt.get('format_id'),
                    'ext': fmt.get('ext'),
                    'resolution': fmt.get('resolution', 'audio only' if fmt.get('vcodec') == 'none' else 'unknown'),
                    'filesize': self._format_file_size(fmt.get('filesize')),
                    'vcodec': fmt.get('vcodec'),
                    'acodec': fmt.get('acodec'),
                    'quality': fmt.get('quality'),
                }
                available_formats.append(format_info)
            
            return {
                "status": "success",
                "message": "Available formats retrieved successfully.",
                "platform": platform,
                "title": info.get('title', 'Unknown'),
                "formats": available_formats[:10]  # Limit to first 10 formats
            }
            
        except Exception as e:
            logger.error(f"Error listing formats: {str(e)}")
            return ErrorResponse(
                message=f"Failed to list formats: {str(e)}",
                platform=platform if 'platform' in locals() else None
            ).dict()
    
    def _format_duration(self, duration: Optional[float]) -> Optional[str]:
        """
        Format duration from seconds to HH:MM:SS.
        
        Args:
            duration (Optional[float]): Duration in seconds
            
        Returns:
            Optional[str]: Formatted duration string
        """
        if duration is None:
            return None
        
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def _format_file_size(self, size_bytes: Optional[int]) -> Optional[str]:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes (Optional[int]): File size in bytes
            
        Returns:
            Optional[str]: Formatted file size string
        """
        if size_bytes is None:
            return None
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    def _get_estimated_file_sizes(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get estimated file sizes for different quality options.
        
        Args:
            info (Dict[str, Any]): Video information from yt-dlp
            
        Returns:
            Dict[str, Any]: File size information for different formats
        """
        formats = info.get('formats', [])
        
        # Find best video and audio formats with file sizes
        best_video = None
        best_audio = None
        video_formats = []
        audio_formats = []
        
        for fmt in formats:
            filesize = fmt.get('filesize') or fmt.get('filesize_approx')
            if not filesize:
                continue
                
            format_info = {
                'format_id': fmt.get('format_id'),
                'ext': fmt.get('ext'),
                'filesize': filesize,
                'filesize_formatted': self._format_file_size(filesize),
                'quality': fmt.get('format_note', ''),
                'resolution': fmt.get('resolution', 'unknown')
            }
            
            # Check if it's video or audio
            if fmt.get('vcodec', 'none') != 'none':  # Has video
                video_formats.append(format_info)
                if not best_video or filesize > best_video.get('filesize', 0):
                    if fmt.get('height', 0) >= 720:  # Prefer HD quality
                        best_video = format_info
            elif fmt.get('acodec', 'none') != 'none':  # Audio only
                audio_formats.append(format_info)
                if not best_audio or filesize > best_audio.get('filesize', 0):
                    best_audio = format_info
        
        # Sort by filesize (largest first)
        video_formats.sort(key=lambda x: x.get('filesize', 0), reverse=True)
        audio_formats.sort(key=lambda x: x.get('filesize', 0), reverse=True)
        
        return {
            'best_video': best_video,
            'best_audio': best_audio,
            'video_options': video_formats[:5],  # Top 5 video formats
            'audio_options': audio_formats[:3],  # Top 3 audio formats
            'estimated_total': self._format_file_size(
                (best_video.get('filesize', 0) if best_video else 0) +
                (best_audio.get('filesize', 0) if best_audio else 0)
            ) if best_video or best_audio else None
        }
    
    def _get_video_quality_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get video quality and technical information.
        
        Args:
            info (Dict[str, Any]): Video information from yt-dlp
            
        Returns:
            Dict[str, Any]: Video quality information
        """
        formats = info.get('formats', [])
        
        # Find the best quality video format
        best_video = None
        available_qualities = set()
        
        for fmt in formats:
            if fmt.get('vcodec', 'none') != 'none':  # Has video
                height = fmt.get('height')
                width = fmt.get('width')
                
                if height:
                    quality_label = f"{height}p"
                    available_qualities.add(quality_label)
                    
                    if not best_video or (height > best_video.get('height', 0)):
                        best_video = {
                            'width': width,
                            'height': height,
                            'resolution': f"{width}x{height}" if width and height else f"{height}p",
                            'fps': fmt.get('fps'),
                            'vcodec': fmt.get('vcodec'),
                            'acodec': fmt.get('acodec'),
                            'ext': fmt.get('ext'),
                            'format_note': fmt.get('format_note', ''),
                            'quality_label': quality_label
                        }
        
        return {
            'best_quality': best_video,
            'available_qualities': sorted(list(available_qualities), 
                                        key=lambda x: int(x.replace('p', '')), reverse=True),
            'has_video': best_video is not None,
            'max_resolution': best_video.get('resolution') if best_video else None,
            'max_fps': best_video.get('fps') if best_video else None
        }
    
    def download(self, url: str, download_type: str) -> Dict[str, Any]:
        """
        Download video or audio from the given URL.
        
        Args:
            url (str): Video URL to download
            download_type (str): Type of download ('video' or 'audio')
            
        Returns:
            Dict[str, Any]: Download result with status, message, and file info
        """
        try:
            # Validate download type
            try:
                dl_type = DownloadType(download_type.lower())
            except ValueError:
                return ErrorResponse(
                    message=f"Invalid download type. Must be 'video' or 'audio', got '{download_type}'"
                ).dict()
            
            # Detect platform
            platform = PlatformDetector.detect_platform(url)
            if not platform:
                return ErrorResponse(
                    message=f"Unsupported platform or invalid URL. Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}",
                    download_type=download_type
                ).dict()
            
            # Extract video information
            info = self._extract_info(url)
            if not info:
                return ErrorResponse(
                    message="Failed to extract video information. The URL might be invalid or the video might be private.",
                    platform=platform,
                    download_type=download_type
                ).dict()
            
            # Get download options
            options = self._get_download_options(dl_type)
            
            # Download the media
            downloaded_files = []
            
            def hook(d):
                if d['status'] == 'finished':
                    downloaded_files.append(d['filename'])
                    logger.info(f"Downloaded: {d['filename']}")
                elif d['status'] == 'processing':
                    logger.info(f"Processing: {d.get('info_dict', {}).get('_filename', 'unknown')}")
            
            def postprocessor_hook(d):
                if d['status'] == 'finished':
                    # This gets called after post-processing (e.g., after audio extraction)
                    processed_file = d.get('info_dict', {}).get('_filename')
                    if processed_file and processed_file not in downloaded_files:
                        downloaded_files.append(processed_file)
                        logger.info(f"Post-processed: {processed_file}")
            
            options['progress_hooks'] = [hook]
            options['postprocessor_hooks'] = [postprocessor_hook]
            
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([url])
            except yt_dlp.DownloadError as e:
                # If download fails due to format issues, try with a more basic format
                logger.warning(f"Initial download failed: {str(e)}")
                logger.info("Trying with fallback format selection...")
                
                # Fallback options with more basic format selection
                fallback_options = options.copy()
                if dl_type == DownloadType.AUDIO:
                    # For audio, try to get any audio stream available
                    fallback_options.update({
                        'format': 'worst[acodec!=none]/bestaudio/worst',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '128',  # Lower quality for fallback
                        }]
                    })
                else:
                    fallback_options['format'] = 'worst[height>=360]/worst'
                
                with yt_dlp.YoutubeDL(fallback_options) as ydl:
                    ydl.download([url])
            
            if not downloaded_files:
                return ErrorResponse(
                    message="Download completed but no files were found.",
                    platform=platform,
                    download_type=download_type
                ).dict()
            
            # Get the downloaded file path
            file_path = downloaded_files[0]
            
            # For audio downloads, check if the file was converted to mp3
            if dl_type == DownloadType.AUDIO:
                # Check if the original file was converted to mp3
                base_name = os.path.splitext(file_path)[0]
                mp3_file = f"{base_name}.mp3"
                if os.path.exists(mp3_file) and file_path != mp3_file:
                    file_path = mp3_file
                    logger.info(f"Using converted audio file: {mp3_file}")
            
            # Ensure the file exists
            if not os.path.exists(file_path):
                return ErrorResponse(
                    message=f"Downloaded file not found: {file_path}",
                    platform=platform,
                    download_type=download_type
                ).dict()
            
            # Get file size
            file_size = None
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                file_size = self._format_file_size(size_bytes)
            
            # Format duration
            duration = self._format_duration(info.get('duration'))
            
            return DownloadResponse(
                status="success",
                message=f"{dl_type.value.capitalize()} downloaded successfully.",
                file_path=os.path.abspath(file_path),
                platform=platform,
                download_type=dl_type.value,
                file_size=file_size,
                duration=duration
            ).dict()
            
        except yt_dlp.DownloadError as e:
            logger.error(f"yt-dlp download error: {str(e)}")
            return ErrorResponse(
                message=f"Download failed: {str(e)}",
                platform=platform if 'platform' in locals() else None,
                download_type=download_type
            ).dict()
            
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            return ErrorResponse(
                message=f"An unexpected error occurred: {str(e)}",
                platform=platform if 'platform' in locals() else None,
                download_type=download_type
            ).dict()
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information without downloading.
        
        Args:
            url (str): Video URL
            
        Returns:
            Dict[str, Any]: Video information or error response
        """
        try:
            # Detect platform
            platform = PlatformDetector.detect_platform(url)
            if not platform:
                return ErrorResponse(
                    message=f"Unsupported platform or invalid URL. Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}"
                ).dict()
            
            # Extract video information
            info = self._extract_info(url)
            if not info:
                return ErrorResponse(
                    message="Failed to extract video information. The URL might be invalid or the video might be private.",
                    platform=platform
                ).dict()
            
            # Get file size information from available formats
            file_size_info = self._get_estimated_file_sizes(info)
            
            # Get video dimensions and quality info
            video_quality = self._get_video_quality_info(info)
            
            return {
                "status": "success",
                "message": "Video information extracted successfully.",
                "platform": platform,
                "title": info.get('title', 'Unknown'),
                "duration": self._format_duration(info.get('duration')),
                "duration_seconds": info.get('duration'),  # Raw duration in seconds
                "view_count": info.get('view_count'),
                "uploader": info.get('uploader', 'Unknown'),
                "upload_date": info.get('upload_date'),
                "description": info.get('description', '')[:200] + '...' if info.get('description') else None,
                "file_sizes": file_size_info,
                "video_quality": video_quality,
                "thumbnail": info.get('thumbnail'),
                "webpage_url": info.get('webpage_url'),
                "format_count": len(info.get('formats', []))
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return ErrorResponse(
                message=f"Failed to get video information: {str(e)}",
                platform=platform if 'platform' in locals() else None
            ).dict()
