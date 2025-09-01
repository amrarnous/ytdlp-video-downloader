# Video Downloader

A comprehensive Python application for downloading videos and audio from multiple platforms including YouTube, Facebook, Twitter/X, Instagram, TikTok, and more.

## Features

- 🎥 **Multi-platform support**: YouTube, Facebook, Twitter/X, Instagram, TikTok, Vimeo, Twitch, Dailymotion
- 🎵 **Audio/Video downloads**: Choose between video (MP4) or audio (MP3) formats
- 🔧 **Multiple interfaces**: Command-line, Python API, and REST API
- 🤖 **Telegram bot support**: Direct binary file endpoint for Telegram bot integration
- 🐳 **Docker support**: Easy deployment with Docker and Docker Compose
- 🛡️ **Error handling**: Comprehensive error handling and validation
- 📋 **Format support**: Common formats with quality options
- 🔍 **Video info**: Get detailed video metadata including file sizes and duration
- 📚 **Well-documented**: Comprehensive documentation and examples

## Quick Start

### Using Docker (Recommended)

1. **Clone and build**:
   ```bash
   git clone <repository-url>
   cd video-downloader
   docker-compose up -d
   ```

2. **Access the API**:
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg**:
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`

## Usage

### Command Line Interface

```bash
# Download video
python -m src.cli "https://www.youtube.com/watch?v=example" --type video

# Download audio
python -m src.cli "https://www.youtube.com/watch?v=example" --type audio

# Get video information
python -m src.cli "https://www.youtube.com/watch?v=example" --info

# Custom output directory
python -m src.cli "https://www.youtube.com/watch?v=example" --output ./my_downloads

# JSON output
python -m src.cli "https://www.youtube.com/watch?v=example" --json
```

### Python API

```python
from src.downloader import VideoDownloader

# Initialize downloader
downloader = VideoDownloader(download_dir="downloads")

# Download video
result = downloader.download(
    url="https://www.youtube.com/watch?v=example",
    download_type="video"
)

print(result)
# Output:
# {
#     "status": "success",
#     "message": "Video downloaded successfully.",
#     "file_path": "/path/to/downloads/video.mp4",
#     "platform": "YouTube",
#     "download_type": "video",
#     "file_size": "25.3 MB",
#     "duration": "03:45"
# }

# Get video info without downloading
info = downloader.get_video_info("https://www.youtube.com/watch?v=example")
print(info)
# Output:
# {
#     "status": "success",
#     "title": "Example Video",
#     "duration": "03:45",
#     "platform": "YouTube",
#     "estimated_size": {
#         "video": "45.2 MB",
#         "audio": "8.1 MB"
#     },
#     "formats": {
#         "video_formats": ["720p", "1080p"],
#         "audio_formats": ["128kbps", "320kbps"]
#     }
# }
```

### REST API

**Download Video/Audio:**
```bash
curl -X POST "http://localhost:8000/download" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.youtube.com/watch?v=example",
       "download_type": "video"
     }'
```

**Download for Telegram Bot (Returns Binary File):**
```bash
curl -X POST "http://localhost:8000/download/telegram" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.youtube.com/watch?v=example",
       "download_type": "video"
     }' \
     --output downloaded_video.mp4
```
*Note: This endpoint returns the actual file binary data, perfect for Telegram bots.*

**Get Video Information (with file size and duration):**
```bash
curl -X POST "http://localhost:8000/info" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

**List Downloaded Files:**
```bash
curl "http://localhost:8000/"
```

## API Documentation

### Available Endpoints

1. **POST /download** - Download and get file information
2. **POST /download/telegram** - Download and return binary file (for bots)
3. **POST /info** - Get video information without downloading
4. **GET /health** - Health check endpoint
5. **GET /** - API information and status

### Response Formats

**Standard Download Response (POST /download):**
```json
{
  "status": "success" | "error",
  "message": "Description of the result",
  "file_path": "path/to/downloaded/file.mp4",
  "platform": "YouTube",
  "download_type": "video" | "audio",
  "file_size": "25.3 MB",
  "duration": "03:45"
}
```

**Telegram Download Response (POST /download/telegram):**
Returns the actual binary file data with appropriate headers for direct use by Telegram bots.

**Video Info Response (POST /info):**
```json
{
  "status": "success",
  "title": "Video Title",
  "description": "Video description...",
  "duration": "03:45",
  "platform": "YouTube",
  "uploader": "Channel Name",
  "view_count": 1000000,
  "upload_date": "2024-01-15",
  "formats": {
    "video_formats": ["720p", "1080p"],
    "audio_formats": ["128kbps", "320kbps"]
  },
  "estimated_size": {
    "video": "45.2 MB",
    "audio": "8.1 MB"
  },
  "thumbnail": "https://example.com/thumbnail.jpg"
}
```

### Error Response Example

```json
{
  "status": "error",
  "message": "Unsupported platform or invalid URL.",
  "file_path": null,
  "platform": null,
  "download_type": "audio"
}
```

**Telegram Bot Integration:**
The `/download/telegram` endpoint returns the actual binary file data directly. This is perfect for Telegram bots as they can:
- Receive the file binary data immediately
- Send it directly to users without additional hosting
- Get proper MIME types and file information via headers
- Handle both video and audio files seamlessly

**Key Benefits for Telegram Bots:**
- **Direct Binary Response**: No need for separate file hosting
- **Proper Headers**: MIME type, filename, and size included
- **Optimized**: Single request gets the file ready for sending
- **Security**: No exposed file URLs or storage management needed

## Supported Platforms

| Platform | Video | Audio | Notes |
|----------|-------|-------|-------|
| YouTube | ✅ | ✅ | Full support |
| Facebook | ✅ | ✅ | Public videos only |
| Twitter/X | ✅ | ✅ | Public tweets |
| Instagram | ✅ | ✅ | Public posts/reels |
| TikTok | ✅ | ✅ | Public videos |
| Vimeo | ✅ | ✅ | Public videos |
| Twitch | ✅ | ✅ | VODs and clips |
| Dailymotion | ✅ | ✅ | Public videos |

## Docker Usage

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Only

```bash
# Build image
docker build -t video-downloader .

# Run container
docker run -d \
  --name video-downloader \
  -p 8000:8000 \
  -v $(pwd)/downloads:/app/downloads \
  video-downloader
```

## Configuration

### Environment Variables

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DOWNLOAD_DIR`: Default download directory
- `MAX_FILE_SIZE`: Maximum file size limit (optional)

### Docker Environment

```yaml
environment:
  - LOG_LEVEL=INFO
  - DOWNLOAD_DIR=/app/downloads
```

## Development

### Project Structure

```
video-downloader/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── api.py               # FastAPI web interface
│   ├── cli.py               # Command-line interface
│   ├── downloader.py        # Core downloader logic
│   ├── models.py            # Pydantic models
│   └── platform_detector.py # Platform detection utilities
├── tests/                   # Test files
├── downloads/               # Downloaded files (created automatically)
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── requirements.txt         # Python dependencies
├── example.py              # Usage examples
└── README.md               # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Adding New Platforms

1. Update `PlatformDetector.PLATFORM_PATTERNS` in `platform_detector.py`
2. Test with the new platform URLs
3. Update documentation

## Troubleshooting

### Common Issues

**FFmpeg not found:**
```bash
# Install FFmpeg
sudo apt install ffmpeg  # Linux
brew install ffmpeg       # macOS
```

**Permission denied:**
```bash
# Fix permissions
chmod +x downloads/
```

**Docker build fails:**
```bash
# Clear Docker cache
docker system prune -a
```

### Platform-Specific Issues

**YouTube:**
- Age-restricted videos may fail
- Private videos are not accessible
- Some videos may require authentication

**Instagram:**
- Private accounts are not accessible
- Stories have limited availability

**TikTok:**
- Regional restrictions may apply
- Some videos may be unavailable

## Legal Compliance

⚠️ **Important Legal Notice**

- Only download content you have permission to download
- Respect copyright laws and platform terms of service
- This tool is for personal use and educational purposes
- Users are responsible for compliance with applicable laws
- Do not distribute downloaded copyrighted content

## Security

- Input validation for all URLs
- No execution of user-provided code
- Sandboxed Docker environment
- Regular security updates for dependencies

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@example.com
- 🐛 Issues: GitHub Issues
- 📚 Documentation: This README and inline docs
- 💬 Discussions: GitHub Discussions

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The core downloading library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [FFmpeg](https://ffmpeg.org/) - Media processing

---

**Disclaimer**: This software is provided "as is" without warranty. Users are responsible for ensuring their use complies with applicable laws and platform terms of service.
