"""
FastAPI Web Interface for Video Downloader

This module provides a REST API interface for the video downloader service.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
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


@app.post("/download/telegram")
async def download_video_telegram(request: DownloadRequest) -> FileResponse:
    """
    Download video or audio from the provided URL and return the binary file for Telegram bot.
    
    This endpoint downloads the file and returns it directly as binary data,
    perfect for Telegram bots that need to send the file to users.
    
    Args:
        request (DownloadRequest): Download request with URL and type
        
    Returns:
        FileResponse: The downloaded file as binary data
    """
    try:
        logger.info(f"Telegram download request: {request.url} ({request.download_type})")
        
        # Download the file
        download_result = downloader.download(str(request.url), request.download_type.value)
        
        if download_result["status"] == "error":
            raise HTTPException(status_code=400, detail={
                "success": False,
                "message": download_result["message"],
                "platform": download_result.get("platform"),
                "download_type": request.download_type.value
            })
        
        # Get the downloaded file path
        file_path = Path(download_result["file_path"])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail={
                "success": False,
                "message": "Downloaded file not found",
                "platform": download_result.get("platform"),
                "download_type": request.download_type.value
            })
        
        # Determine MIME type based on file extension and download type
        if request.download_type == DownloadType.VIDEO:
            if file_path.name.endswith('.mp4'):
                media_type = "video/mp4"
            elif file_path.name.endswith('.webm'):
                media_type = "video/webm"
            elif file_path.name.endswith('.mkv'):
                media_type = "video/x-matroska"
            else:
                media_type = "video/mp4"
        else:  # audio
            if file_path.name.endswith('.mp3'):
                media_type = "audio/mpeg"
            elif file_path.name.endswith('.m4a'):
                media_type = "audio/mp4"
            elif file_path.name.endswith('.ogg'):
                media_type = "audio/ogg"
            else:
                media_type = "audio/mpeg"
        
        # Return the file as binary data
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_path.name}",
                "X-Platform": download_result.get("platform", "unknown"),
                "X-Download-Type": request.download_type.value,
                "X-File-Size": str(file_path.stat().st_size),
                "Cache-Control": "private, max-age=3600"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in Telegram download endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail={
            "success": False,
            "message": f"Internal server error: {str(e)}",
            "platform": None,
            "download_type": request.download_type.value if request else None
        })


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
