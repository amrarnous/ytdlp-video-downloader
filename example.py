"""
Simple Usage Example

This script demonstrates basic usage of the video downloader.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.downloader import VideoDownloader
from src.platform_detector import PlatformDetector


def main():
    """Demonstrate basic usage."""
    
    # Initialize downloader
    downloader = VideoDownloader(download_dir="downloads")
    
    # Example URLs (you would replace these with actual URLs)
    example_urls = [
        # Note: These are example URLs - replace with actual working URLs for testing
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Never Gonna Give You Up
        "https://vimeo.com/123456789"  # Example Vimeo URL
    ]
    
    print("Video Downloader Example")
    print("=" * 50)
    print(f"Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}")
    print()
    
    # Interactive mode
    while True:
        print("Options:")
        print("1. Download video")
        print("2. Download audio")
        print("3. Get video info")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "4":
            print("Goodbye!")
            break
            
        if choice not in ["1", "2", "3"]:
            print("Invalid choice. Please try again.")
            continue
            
        url = input("Enter video URL: ").strip()
        
        if not url:
            print("URL cannot be empty.")
            continue
            
        # Check if platform is supported
        platform = PlatformDetector.detect_platform(url)
        if not platform:
            print(f"Unsupported platform. Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}")
            continue
            
        print(f"Detected platform: {platform}")
        
        if choice == "3":
            # Get video info
            print("\nGetting video information...")
            result = downloader.get_video_info(url)
            
            if result["status"] == "success":
                print(f"✓ Title: {result.get('title', 'Unknown')}")
                print(f"  Duration: {result.get('duration', 'Unknown')}")
                print(f"  Uploader: {result.get('uploader', 'Unknown')}")
                if result.get('view_count'):
                    print(f"  Views: {result['view_count']:,}")
            else:
                print(f"✗ Error: {result['message']}")
                
        else:
            # Download video or audio
            download_type = "video" if choice == "1" else "audio"
            print(f"\nDownloading {download_type}...")
            
            result = downloader.download(url, download_type)
            
            if result["status"] == "success":
                print(f"✓ {result['message']}")
                print(f"  File: {result['file_path']}")
                if result.get('file_size'):
                    print(f"  Size: {result['file_size']}")
                if result.get('duration'):
                    print(f"  Duration: {result['duration']}")
            else:
                print(f"✗ Error: {result['message']}")
        
        print()


if __name__ == "__main__":
    main()
