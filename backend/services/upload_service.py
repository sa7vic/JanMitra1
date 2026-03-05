"""
Cloudinary upload service for report photo attachments.
"""
import cloudinary
import cloudinary.uploader
from flask import current_app
import os


ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'heic'}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB default


def _configure_cloudinary():
    """Lazily configure Cloudinary from Flask app config."""
    cloudinary.config(
        cloud_name=current_app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key=current_app.config.get('CLOUDINARY_API_KEY'),
        api_secret=current_app.config.get('CLOUDINARY_API_SECRET'),
        secure=True,
    )


def allowed_file(filename: str) -> bool:
    """Return True if the filename has an accepted image extension."""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_image_file(file_storage):
    """
    Validate a Werkzeug FileStorage object.

    Returns (ok: bool, error_message: str | None)
    """
    if file_storage is None or file_storage.filename == '':
        return False, 'No file selected'

    if not allowed_file(file_storage.filename):
        return False, (
            f'Invalid file type. Allowed types: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        )

    # Check size by reading into memory (file not yet consumed)
    file_storage.seek(0, 2)  # Seek to end
    size = file_storage.tell()
    file_storage.seek(0)     # Rewind

    max_size = current_app.config.get('MAX_UPLOAD_SIZE_MB', 5) * 1024 * 1024
    if size > max_size:
        max_mb = current_app.config.get('MAX_UPLOAD_SIZE_MB', 5)
        return False, f'File too large. Maximum allowed size is {max_mb} MB'

    return True, None


def upload_report_image(file_storage, report_id: int = None) -> dict:
    """
    Upload an image file to Cloudinary under the /reports folder.

    Args:
        file_storage: Werkzeug FileStorage object from request.files
        report_id:    Optional report ID used to build the public_id

    Returns:
        dict with keys: url, public_id, width, height, format, bytes
    """
    _configure_cloudinary()

    public_id = f'reports/{report_id}' if report_id else 'reports/temp'

    result = cloudinary.uploader.upload(
        file_storage,
        folder='janmitra/reports',
        public_id=f'report_{report_id}' if report_id else None,
        overwrite=True,
        resource_type='image',
        transformation=[
            # Limit stored image to 1920px wide max, good quality
            {'width': 1920, 'crop': 'limit', 'quality': 'auto:good', 'fetch_format': 'auto'}
        ],
    )

    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'width': result.get('width'),
        'height': result.get('height'),
        'format': result.get('format'),
        'bytes': result.get('bytes'),
    }


def delete_report_image(public_id: str) -> bool:
    """Delete an image from Cloudinary by its public_id."""
    _configure_cloudinary()
    result = cloudinary.uploader.destroy(public_id, resource_type='image')
    return result.get('result') == 'ok'
