"""
Command Line Interface for Video Downloader

This module provides a CLI interface for the video downloader service.
"""

import argparse
import json
import sys
from pathlib import Path
from .downloader import VideoDownloader
from .platform_detector import PlatformDetector


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Download videos and audio from various platforms",
        epilog="Example: python -m src.cli https://www.youtube.com/watch?v=example --type audio"
    )
    
    parser.add_argument(
        "url",
        help="Video URL to download"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["video", "audio"],
        default="video",
        help="Download type: video or audio (default: video)"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="downloads",
        help="Output directory (default: downloads)"
    )
    
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="Get video information without downloading"
    )
    
    parser.add_argument(
        "--platforms",
        action="store_true",
        help="List supported platforms"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result in JSON format"
    )
    
    args = parser.parse_args()
    
    # List supported platforms
    if args.platforms:
        platforms = PlatformDetector.get_supported_platforms()
        if args.json:
            print(json.dumps({"supported_platforms": platforms}, indent=2))
        else:
            print("Supported platforms:")
            for platform in platforms:
                print(f"  - {platform}")
        return
    
    # Initialize downloader
    downloader = VideoDownloader(download_dir=args.output)
    
    try:
        if args.info:
            # Get video information
            result = downloader.get_video_info(args.url)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["status"] == "success":
                    print(f"Title: {result.get('title', 'Unknown')}")
                    print(f"Platform: {result.get('platform', 'Unknown')}")
                    print(f"Duration: {result.get('duration', 'Unknown')}")
                    print(f"Uploader: {result.get('uploader', 'Unknown')}")
                    if result.get('view_count'):
                        print(f"Views: {result['view_count']:,}")
                    if result.get('description'):
                        print(f"Description: {result['description']}")
                else:
                    print(f"Error: {result['message']}")
                    sys.exit(1)
        else:
            # Download video/audio
            result = downloader.download(args.url, args.type)
            
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if result["status"] == "success":
                    print(f"✓ {result['message']}")
                    print(f"Platform: {result['platform']}")
                    print(f"Type: {result['download_type']}")
                    print(f"File: {result['file_path']}")
                    if result.get('file_size'):
                        print(f"Size: {result['file_size']}")
                    if result.get('duration'):
                        print(f"Duration: {result['duration']}")
                else:
                    print(f"✗ Error: {result['message']}")
                    sys.exit(1)
                    
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        if args.json:
            error_result = {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"✗ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
