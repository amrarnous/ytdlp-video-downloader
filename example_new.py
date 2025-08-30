#!/usr/bin/env python3
"""
Example usage of the Video Downloader

This script demonstrates how to use the VideoDownloader class
to download videos and audio from various platforms.
"""

import json
from src.downloader import VideoDownloader
from src.platform_detector import PlatformDetector


def display_result(result):
    """Display download result in a formatted way."""
    if result["status"] == "success":
        print(f"✓ {result['message']}")
        print(f"  File: {result['file_path']}")
        if result.get('file_size'):
            print(f"  Size: {result['file_size']}")
        if result.get('duration'):
            print(f"  Duration: {result['duration']}")
        print(f"  Platform: {result.get('platform', 'Unknown')}")
    else:
        print(f"✗ Error: {result['message']}")


def display_video_info(result):
    """Display video information in a formatted way."""
    if result["status"] == "success":
        print(f"✓ Video Information:")
        print(f"  Title: {result.get('title', 'Unknown')}")
        print(f"  Platform: {result.get('platform', 'Unknown')}")
        print(f"  Duration: {result.get('duration', 'Unknown')}")
        print(f"  Uploader: {result.get('uploader', 'Unknown')}")
        if result.get('view_count'):
            print(f"  Views: {result['view_count']:,}")
        if result.get('upload_date'):
            print(f"  Upload Date: {result['upload_date']}")
        if result.get('description'):
            print(f"  Description: {result['description']}")
    else:
        print(f"✗ Error: {result['message']}")


def display_formats(result):
    """Display available formats in a formatted way."""
    if result["status"] == "success":
        print(f"✓ Available formats for: {result.get('title', 'Unknown')}")
        print(f"  Platform: {result.get('platform', 'Unknown')}")
        print("\n  Formats:")
        
        formats = result.get('formats', [])
        if not formats:
            print("    No formats found.")
            return
            
        # Display headers
        print(f"    {'ID':<15} {'Ext':<8} {'Resolution':<15} {'Size':<12} {'Video':<12} {'Audio':<12}")
        print(f"    {'-'*15} {'-'*8} {'-'*15} {'-'*12} {'-'*12} {'-'*12}")
        
        for fmt in formats:
            format_id = fmt.get('format_id', 'N/A')[:14]
            ext = fmt.get('ext', 'N/A')[:7]
            resolution = fmt.get('resolution', 'N/A')[:14]
            filesize = fmt.get('filesize', 'N/A')[:11] if fmt.get('filesize') != 'N/A' else 'N/A'
            vcodec = fmt.get('vcodec', 'N/A')[:11]
            acodec = fmt.get('acodec', 'N/A')[:11]
            
            print(f"    {format_id:<15} {ext:<8} {resolution:<15} {filesize:<12} {vcodec:<12} {acodec:<12}")
    else:
        print(f"✗ Error: {result['message']}")


def main():
    """Main function to demonstrate the video downloader."""
    downloader = VideoDownloader()
    
    print("Video Downloader Example")
    print("=" * 50)
    print(f"Supported platforms: {', '.join(PlatformDetector.get_supported_platforms())}")
    print()
    
    while True:
        print("Options:")
        print("1. Download video")
        print("2. Download audio")
        print("3. Get video info")
        print("4. List available formats")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '5':
            print("Goodbye!")
            break
        
        if choice not in ['1', '2', '3', '4']:
            print("❌ Invalid choice. Please enter 1-5.")
            continue
        
        url = input("Enter video URL: ").strip()
        if not url:
            print("❌ URL cannot be empty.")
            continue
        
        # Detect and display platform
        platform = PlatformDetector.detect_platform(url)
        if platform:
            print(f"Detected platform: {platform}")
        else:
            print("❌ Unsupported platform or invalid URL.")
            continue
        
        if choice == '1':
            print("\nDownloading video...")
            result = downloader.download(url, "video")
            display_result(result)
            
        elif choice == '2':
            print("\nDownloading audio...")
            result = downloader.download(url, "audio")
            display_result(result)
            
        elif choice == '3':
            print("\nGetting video info...")
            result = downloader.get_video_info(url)
            display_video_info(result)
            
        elif choice == '4':
            print("\nListing available formats...")
            result = downloader.list_formats(url)
            display_formats(result)
        
        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
