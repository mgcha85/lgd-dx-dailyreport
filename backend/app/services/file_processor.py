import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import shutil


ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.pptx', '.xlsb'}


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    """Save uploaded file to destination"""
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return destination
    finally:
        upload_file.file.close()


def create_unique_filename(original_filename: str, directory: Path) -> Path:
    """Create unique filename to avoid conflicts"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = Path(original_filename).stem
    ext = Path(original_filename).suffix
    
    unique_filename = f"{name}_{timestamp}{ext}"
    return directory / unique_filename


def cleanup_file(file_path: str) -> bool:
    """Delete file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False
