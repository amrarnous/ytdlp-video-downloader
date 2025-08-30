"""
FastAPI Web Interface for Video Downloader

This module provides a REST API interface for the video downloader service.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .downloader import VideoDownloader
from .models import DownloadRequest, DownloadResponse, ErrorResponse, TelegramDownloadResponse, DownloadType


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Video Downloader API",
    description="A multi-platform video and audio downloader service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize downloader
downloader = VideoDownloader()


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Video Downloader API",
        "version": "1.0.0",
        "supported_platforms": [
            "YouTube", "Facebook", "Twitter/X", "Instagram", 
            "TikTok", "Vimeo", "Twitch", "Dailymotion"
        ],
        "endpoints": {
            "download": "/download",
            "download_telegram": "/download/telegram",
            "info": "/info",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Service is running"}


@app.post("/download", response_model=DownloadResponse)
async def download_video(request: DownloadRequest) -> JSONResponse:
    """
    Download video or audio from the provided URL.
    
    Args:
        request (DownloadRequest): Download request with URL and type
        
    Returns:
        JSONResponse: Download result with file information
    """
    try:
        logger.info(f"Download request: {request.url} ({request.download_type})")
        
        result = downloader.download(str(request.url), request.download_type.value)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in download endpoint: {str(e)}")
        error_response = ErrorResponse(
            message=f"Internal server error: {str(e)}"
        ).dict()
        raise HTTPException(status_code=500, detail=error_response)


@app.post("/download/telegram", response_model=TelegramDownloadResponse)
async def download_video_telegram(request: DownloadRequest) -> JSONResponse:
    """
    Download video or audio from the provided URL with Telegram bot compatible response.
    
    This endpoint returns a response format optimized for Telegram bot integration,
    including proper file URLs, MIME types, and metadata that Telegram bots expect.
    
    Args:
        request (DownloadRequest): Download request with URL and type
        
    Returns:
        JSONResponse: Telegram-compatible download result
    """
    try:
        logger.info(f"Telegram download request: {request.url} ({request.download_type})")
        
        # First get video info for metadata
        info_result = downloader.get_video_info(str(request.url))
        
        # Then download the file
        download_result = downloader.download(str(request.url), request.download_type.value)
        
        if download_result["status"] == "error":
            return JSONResponse(content={
                "success": False,
                "message": download_result["message"],
                "file_url": None,
                "file_name": None,
                "file_size": None,
                "duration": None,
                "width": None,
                "height": None,
                "thumbnail": None,
                "mime_type": None,
                "platform": download_result.get("platform"),
                "download_type": request.download_type.value,
                "title": None,
                "description": None
            })
        
        # Extract file information
        file_path = Path(download_result["file_path"])
        file_name = file_path.name
        file_size = file_path.stat().st_size if file_path.exists() else None
        
        # Generate file URL for serving
        file_url = f"http://localhost:8000/download/{file_name}"
        
        # Determine MIME type based on file extension and download type
        if request.download_type == DownloadType.VIDEO:
            if file_name.endswith('.mp4'):
                mime_type = "video/mp4"
            elif file_name.endswith('.webm'):
                mime_type = "video/webm"
            elif file_name.endswith('.mkv'):
                mime_type = "video/x-matroska"
            else:
                mime_type = "video/mp4"
        else:  # audio
            if file_name.endswith('.mp3'):
                mime_type = "audio/mpeg"
            elif file_name.endswith('.m4a'):
                mime_type = "audio/mp4"
            elif file_name.endswith('.ogg'):
                mime_type = "audio/ogg"
            else:
                mime_type = "audio/mpeg"
        
        # Parse duration from the info or download result
        duration_seconds = None
        if info_result.get("status") == "success" and info_result.get("duration"):
            duration_str = info_result.get("duration", "")
            try:
                # Parse duration like "03:45" to seconds
                if ":" in duration_str:
                    parts = duration_str.split(":")
                    if len(parts) == 2:  # MM:SS
                        duration_seconds = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:  # HH:MM:SS
                        duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except (ValueError, IndexError):
                duration_seconds = None
        
        # Extract video dimensions for video files (if available)
        width, height = None, None
        if request.download_type == DownloadType.VIDEO and info_result.get("status") == "success":
            # These would come from video metadata if available
            # For now, set common defaults
            width = 1280
            height = 720
        
        # Build Telegram-compatible response
        telegram_response = {
            "success": True,
            "message": f"{request.download_type.value.title()} downloaded successfully for Telegram bot",
            "file_url": file_url,
            "file_name": file_name,
            "file_size": file_size,
            "duration": duration_seconds,
            "width": width,
            "height": height,
            "thumbnail": None,  # Could be extracted from video metadata
            "mime_type": mime_type,
            "platform": download_result.get("platform"),
            "download_type": request.download_type.value,
            "title": info_result.get("title") if info_result.get("status") == "success" else None,
            "description": info_result.get("description") if info_result.get("status") == "success" else None
        }
        
        return JSONResponse(content=telegram_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Telegram download endpoint: {str(e)}")
        error_response = {
            "success": False,
            "message": f"Internal server error: {str(e)}",
            "file_url": None,
            "file_name": None,
            "file_size": None,
            "duration": None,
            "width": None,
            "height": None,
            "thumbnail": None,
            "mime_type": None,
            "platform": None,
            "download_type": request.download_type.value if request else None,
            "title": None,
            "description": None
        }
        raise HTTPException(status_code=500, detail=error_response)


@app.post("/info")
async def get_video_info(request: Dict[str, str]) -> JSONResponse:
    """
    Get video information without downloading.
    
    Args:
        request (Dict[str, str]): Request with URL
        
    Returns:
        JSONResponse: Video information
    """
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(
                status_code=400, 
                detail={"message": "URL is required"}
            )
        
        logger.info(f"Info request: {url}")
        
        result = downloader.get_video_info(url)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in info endpoint: {str(e)}")
        error_response = ErrorResponse(
            message=f"Internal server error: {str(e)}"
        ).dict()
        raise HTTPException(status_code=500, detail=error_response)


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a previously downloaded file.
    
    Args:
        filename (str): Name of the file to download
        
    Returns:
        FileResponse: The requested file
    """
    try:
        file_path = downloader.download_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404, 
                detail={"message": f"File '{filename}' not found"}
            )
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"message": f"Error serving file: {str(e)}"}
        )


@app.get("/files")
async def list_files():
    """
    List all downloaded files.
    
    Returns:
        JSONResponse: List of available files
    """
    try:
        files = []
        for file_path in downloader.download_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "created": stat.st_ctime,
                    "download_url": f"/download/{file_path.name}"
                })
        
        return JSONResponse(content={
            "status": "success",
            "files": files,
            "count": len(files)
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": f"Error listing files: {str(e)}"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
