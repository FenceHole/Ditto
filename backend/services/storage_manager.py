"""
Storage Manager Service
Handles file uploads and storage
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
from datetime import datetime
from fastapi import UploadFile


class StorageManager:
    """Manages file storage for uploaded images"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "storage",
            "uploads"
        )
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create storage directories if they don't exist"""
        Path(self.base_path).mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> str:
        """
        Save uploaded file to storage

        Args:
            file: Uploaded file from FastAPI

        Returns:
            Path to saved file
        """
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"

        # Create date-based subdirectory
        date_dir = datetime.now().strftime("%Y/%m/%d")
        full_dir = os.path.join(self.base_path, date_dir)
        Path(full_dir).mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = os.path.join(full_dir, unique_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_path

    def get_file_path(self, relative_path: str) -> str:
        """Get absolute path from relative path"""
        return os.path.join(self.base_path, relative_path)

    def delete_file(self, file_path: str) -> bool:
        """
        Delete file from storage

        Args:
            file_path: Path to file

        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {str(e)}")
            return False

    def get_file_url(self, file_path: str) -> str:
        """
        Get URL for accessing file

        Args:
            file_path: Local file path

        Returns:
            URL or relative path for file access
        """
        # In production, this would return a CDN URL or S3 URL
        # For now, return relative path
        return file_path.replace(self.base_path, "/uploads")

    def cleanup_old_files(self, days: int = 30):
        """
        Clean up files older than specified days

        Args:
            days: Delete files older than this many days
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_time < cutoff_date:
                    try:
                        os.remove(file_path)
                        print(f"Deleted old file: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {str(e)}")
