#!/usr/bin/env python3
"""
Test script for Telegram API endpoint

This script demonstrates how to use the /download/telegram endpoint
which returns responses formatted for Telegram bot integration.
"""

import requests
import json
import time


def test_telegram_endpoint():
    """Test the Telegram-compatible download endpoint."""
    
    # API endpoint
    base_url = "http://localhost:8000"
    telegram_endpoint = f"{base_url}/download/telegram"
    
    print("🤖 Testing Telegram Download API")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "name": "YouTube Video Download",
            "url": "https://www.youtube.com/watch?v=swAicg0GjNg",
            "download_type": "video"
        },
        {
            "name": "YouTube Audio Download", 
            "url": "https://www.youtube.com/watch?v=swAicg0GjNg",
            "download_type": "audio"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"📎 URL: {test_case['url']}")
        print(f"📁 Type: {test_case['download_type']}")
        print("-" * 30)
        
        # Prepare request
        payload = {
            "url": test_case["url"],
            "download_type": test_case["download_type"]
        }
        
        try:
            # Make request
            print("⏳ Making request...")
            response = requests.post(
                telegram_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            # Parse response
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print("\n📋 Telegram Response Format:")
                print(json.dumps(result, indent=2))
                
                # Show what Telegram bot would receive
                print("\n🤖 For Telegram Bot Usage:")
                if result.get("success"):
                    print(f"✓ File URL: {result.get('file_url')}")
                    print(f"✓ File Name: {result.get('file_name')}")
                    print(f"✓ File Size: {result.get('file_size')} bytes")
                    print(f"✓ MIME Type: {result.get('mime_type')}")
                    if result.get('duration'):
                        print(f"✓ Duration: {result.get('duration')} seconds")
                    if result.get('width') and result.get('height'):
                        print(f"✓ Resolution: {result.get('width')}x{result.get('height')}")
                    if result.get('title'):
                        print(f"✓ Title: {result.get('title')}")
                else:
                    print(f"❌ Error: {result.get('message')}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error response: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("⏰ Request timed out (60s)")
        except requests.exceptions.ConnectionError:
            print("🔌 Connection error - is the API server running?")
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            
        if i < len(test_cases):
            print("\n⏳ Waiting 2 seconds before next test...")
            time.sleep(2)


def test_api_info():
    """Test API info endpoint."""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            info = response.json()
            print("📊 API Info:")
            print(json.dumps(info, indent=2))
        else:
            print(f"❌ API not available (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Cannot connect to API: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Telegram API Test")
    print("Make sure the API server is running with: docker-compose up -d")
    print("")
    
    # Test API availability
    test_api_info()
    print("")
    
    # Test Telegram endpoint
    test_telegram_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
    print("\n💡 Usage in Telegram Bot:")
    print("1. Use the file_url to send files via URL")
    print("2. Use file_name, file_size, mime_type for proper file handling")
    print("3. Use duration for audio/video metadata")
    print("4. Use width/height for video dimensions")
