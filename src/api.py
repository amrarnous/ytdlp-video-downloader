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
from .models import DownloadRequest, DownloadResponse, ErrorResponse


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
