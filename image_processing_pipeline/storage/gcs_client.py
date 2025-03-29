"""
Google Cloud Storage client module for the receipt processing pipeline.
Handles downloading images from buckets and generating signed URLs.
"""

import io
import logging
import mimetypes
from typing import Any, Dict, Optional, Tuple

from google.cloud import storage
from google.cloud.exceptions import NotFound
from google.cloud.storage.blob import Blob

# Set up logger
logger = logging.getLogger(__name__)

# Valid image MIME types
VALID_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/tiff',
    'image/gif',
    'image/bmp',
    'image/webp'
]

class GCSClient:
    """Client for interacting with Google Cloud Storage."""
    
    def __init__(self):
        """Initialize the Google Cloud Storage client."""
        try:
            self.client = storage.Client()
            logger.info("GCS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise
    
    def download_image(self, bucket_name: str, blob_name: str) -> Tuple[bytes, str]:
        """
        Download an image from Cloud Storage.
        
        Args:
            bucket_name: Name of the bucket
            blob_name: Path to the image within the bucket
            
        Returns:
            Tuple containing (image_bytes, mime_type)
            
        Raises:
            ValueError: If file is not an image or doesn't exist
            IOError: If download fails
        """
        try:
            # Get bucket reference
            bucket = self.client.bucket(bucket_name)
            
            # Get blob reference
            blob = bucket.blob(blob_name)
            
            # Check if blob exists
            if not blob.exists():
                logger.error(f"Image {blob_name} not found in bucket {bucket_name}")
                raise ValueError(f"Image {blob_name} not found in bucket {bucket_name}")
                
            # Try to reload metadata if needed
            try:
                if blob.size is None:
                    blob.reload()
            except Exception as reload_error:
                logger.warning(f"Failed to reload blob metadata: {reload_error}")
            
            # Check file size
            if blob.size is not None and blob.size > 10 * 1024 * 1024:  # 10MB limit
                logger.warning(f"Image {blob_name} is large ({blob.size / 1024 / 1024:.2f}MB)")
            elif blob.size is None:
                logger.warning(f"Image {blob_name} size unknown (metadata not available)")
            
            # Get content type
            content_type = blob.content_type
            if not content_type:
                # Try to guess from file extension
                content_type, _ = mimetypes.guess_type(blob_name)
                if not content_type:
                    # Default to JPEG if we can't determine
                    content_type = 'image/jpeg'
            
            # Validate that it's an image
            if content_type not in VALID_IMAGE_TYPES:
                logger.error(f"File {blob_name} is not a valid image type: {content_type}")
                raise ValueError(f"File {blob_name} is not a valid image type: {content_type}")
            
            # Download as bytes using a memory buffer
            in_memory_file = io.BytesIO()
            blob.download_to_file(in_memory_file)
            in_memory_file.seek(0)
            
            logger.info(f"Successfully downloaded image {blob_name} from bucket {bucket_name}")
            return in_memory_file.read(), content_type
            
        except NotFound:
            logger.error(f"Bucket {bucket_name} not found")
            raise ValueError(f"Bucket {bucket_name} not found")
        except Exception as e:
            logger.error(f"Error downloading image {blob_name} from bucket {bucket_name}: {e}")
            raise IOError(f"Error downloading image: {e}")
    
    def get_image_metadata(self, bucket_name: str, blob_name: str) -> Dict[str, Any]:
        """
        Get metadata for an image file.
        
        Args:
            bucket_name: Name of the bucket
            blob_name: Path to the image within the bucket
            
        Returns:
            Dictionary of metadata
            
        Raises:
            ValueError: If file doesn't exist
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                raise ValueError(f"Image {blob_name} not found in bucket {bucket_name}")
            
            # Get basic metadata
            metadata = {
                'name': blob_name,
                'size': blob.size,
                'updated': blob.updated,
                'content_type': blob.content_type,
                'md5_hash': blob.md5_hash,
                'generation': blob.generation,
                'metadata': blob.metadata or {}
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting metadata for {blob_name} in {bucket_name}: {e}")
            raise
    
    def update_metadata(self, bucket_name: str, blob_name: str, metadata: Dict[str, str]) -> None:
        """
        Update custom metadata for a file.
        
        Args:
            bucket_name: Name of the bucket
            blob_name: Path to the file within the bucket
            metadata: Dictionary of metadata to set
            
        Raises:
            ValueError: If file doesn't exist
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                raise ValueError(f"File {blob_name} not found in bucket {bucket_name}")
            
            # Update metadata
            blob.metadata = metadata
            blob.patch()
            
            logger.info(f"Updated metadata for {blob_name} in bucket {bucket_name}")
            
        except Exception as e:
            logger.error(f"Error updating metadata for {blob_name} in {bucket_name}: {e}")
            raise
    
    def generate_signed_url(self, bucket_name: str, blob_name: str, expiration_seconds: int = 3600) -> str:
        """
        Generate a signed URL for temporary access to an image.
        
        Args:
            bucket_name: Name of the bucket
            blob_name: Path to the image within the bucket
            expiration_seconds: Time in seconds until URL expires (default: 1 hour)
            
        Returns:
            Signed URL string
            
        Raises:
            ValueError: If file doesn't exist
        """
        try:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            if not blob.exists():
                raise ValueError(f"Image {blob_name} not found in bucket {bucket_name}")
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration_seconds,
                method="GET"
            )
            
            logger.info(f"Generated signed URL for {blob_name} in {bucket_name} (expires in {expiration_seconds}s)")
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL for {blob_name} in {bucket_name}: {e}")
            raise

# Singleton instance for use throughout the application
gcs_client = GCSClient()

def download_image(bucket_name: str, blob_name: str) -> Tuple[bytes, str]:
    """Convenience function to download an image using the singleton client."""
    return gcs_client.download_image(bucket_name, blob_name)

def get_image_metadata(bucket_name: str, blob_name: str) -> Dict[str, Any]:
    """Convenience function to get image metadata using the singleton client."""
    return gcs_client.get_image_metadata(bucket_name, blob_name)

def update_metadata(bucket_name: str, blob_name: str, metadata: Dict[str, str]) -> None:
    """Convenience function to update metadata using the singleton client."""
    return gcs_client.update_metadata(bucket_name, blob_name, metadata)

def generate_signed_url(bucket_name: str, blob_name: str, expiration_seconds: int = 3600) -> str:
    """Convenience function to generate a signed URL using the singleton client."""
    return gcs_client.generate_signed_url(bucket_name, blob_name, expiration_seconds)