"""
Utility functions for file handling and validation
"""
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import current_app

logger = logging.getLogger(__name__)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


def save_uploaded_file(file, custom_filename=None):
    """
    Save uploaded file with a secure filename.

    Args:
        file: The uploaded file object
        custom_filename: Optional custom filename

    Returns:
        Tuple of (success, filename, message)
    """
    try:
        logger.info("Starting file upload process")

        if not file or file.filename == '':
            logger.error("No file provided or empty filename")
            return False, None, 'No file selected'

        logger.info(f"Processing file: {file.filename}")
        logger.debug(
            f"File size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")

        if not allowed_file(file.filename):
            logger.error(f"File type not allowed: {file.filename}")
            return False, None, 'File type not allowed'

        if custom_filename:
            filename = secure_filename(custom_filename)
            logger.debug(f"Using custom filename: {filename}")
        else:
            # Generate unique filename
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            logger.debug(f"Generated unique filename: {filename}")

        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        logger.debug(f"Saving file to: {file_path}")

        # Ensure upload directory exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)

        file.save(file_path)

        # Verify file was saved
        if os.path.exists(file_path):
            saved_size = os.path.getsize(file_path)
            logger.info(
                f"File saved successfully: {filename}, size: {saved_size} bytes")
        else:
            logger.error(f"File was not saved properly: {file_path}")
            return False, None, 'File was not saved properly'

        return True, filename, 'File uploaded successfully'

    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False, None, f'Error saving file: {str(e)}'


def get_file_path(filename):
    """Get the full path for a filename in the upload folder."""
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)


def delete_file(filename):
    """Delete a file from the upload folder."""
    try:
        file_path = get_file_path(filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(filename):
    """Get file size in bytes."""
    try:
        file_path = get_file_path(filename)
        return os.path.getsize(file_path)
    except Exception:
        return 0


def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"
