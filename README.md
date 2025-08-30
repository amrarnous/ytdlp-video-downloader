# Video Downloader

A comprehensive Python application for downloading videos and audio from multiple platforms including YouTube, Facebook, Twitter/X, Instagram, TikTok, and more.

## Features

- 🎥 **Multi-platform support**: YouTube, Facebook, Twitter/X, Instagram, TikTok, Vimeo, Twitch, Dailymotion
- 🎵 **Audio/Video downloads**: Choose between video (MP4) or audio (MP3) formats
- 🔧 **Multiple interfaces**: Command-line, Python API, and REST API
- 🐳 **Docker support**: Easy deployment with Docker and Docker Compose
- 🛡️ **Error handling**: Comprehensive error handling and validation
- 📋 **Format support**: Common formats with quality options
- 🔍 **Video info**: Get video metadata without downloading
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

**Download for Telegram Bot (Optimized Response):**
```bash
curl -X POST "http://localhost:8000/download/telegram" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.youtube.com/watch?v=example",
       "download_type": "video"
     }'
```

**Get Video Information:**
```bash
curl -X POST "http://localhost:8000/info" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=example"}'
```

**List Downloaded Files:**
```bash
curl "http://localhost:8000/files"
```

## API Documentation

### Response Format

All API responses follow this structure:

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

### Telegram Bot Response Format

The `/download/telegram` endpoint returns a response optimized for Telegram bot integration:

```json
{
  "success": true,
  "message": "Video downloaded successfully for Telegram bot",
  "file_url": "http://localhost:8000/download/video.mp4",
  "file_name": "video.mp4",
  "file_size": 26542080,
  "duration": 225,
  "width": 1280,
  "height": 720,
  "thumbnail": null,
  "mime_type": "video/mp4",
  "platform": "YouTube",
  "download_type": "video",
  "title": "Sample Video Title",
  "description": "Video description..."
}
```

**Telegram Bot Integration Fields:**
- `success`: Boolean indicating if download was successful
- `file_url`: Direct URL to download the file
- `file_name`: Original filename for Telegram
- `file_size`: File size in bytes (required by Telegram)
- `duration`: Duration in seconds for audio/video
- `width`/`height`: Video dimensions for Telegram video messages
- `mime_type`: Proper MIME type for Telegram file handling
- `title`: Video title for captions
- `description`: Video description for captions

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
