"""
Storage package for the receipt processing pipeline.
Provides functionality for interacting with cloud storage services.
"""

from storage.gcs_client import (
    GCSClient,
    download_image,
    generate_signed_url,
    get_image_metadata,
    update_metadata,
)

__all__ = [
    'download_image',
    'get_image_metadata',
    'update_metadata',
    'generate_signed_url',
    'GCSClient'
]