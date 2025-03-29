"""
OCR processing pipeline that coordinates the image processing and text extraction.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from models.receipt import Receipt
from ocr.image_utils import enhance_for_receipt, preprocess_image
from ocr.text_parser import clean_text, format_text_blocks
from ocr.vision_client import analyze_document
from storage.gcs_client import download_image, generate_signed_url

# Set up logger
logger = logging.getLogger(__name__)

def process_receipt_image(bucket_name: str, blob_name: str) -> Dict[str, Any]:
    """
    Process a receipt image from Google Cloud Storage.
    
    Args:
        bucket_name: Name of the GCS bucket
        blob_name: Name of the image blob in the bucket
        
    Returns:
        Dictionary with processed OCR results
        
    Raises:
        Exception: If processing fails
    """
    try:
        logger.info(f"Starting OCR processing for {blob_name} in bucket {bucket_name}")
        
        # Step 1: Download the image from GCS
        image_bytes, content_type = download_image(bucket_name, blob_name)
        logger.info(f"Downloaded image ({len(image_bytes)} bytes, type: {content_type})")
        
        # Step 2: Preprocess the image to improve OCR accuracy
        preprocessed_image = enhance_for_receipt(image_bytes)
        logger.info(f"Preprocessed image for receipt OCR ({len(preprocessed_image)} bytes)")
        
        # Step 3: Perform OCR using Cloud Vision API
        ocr_result = analyze_document(preprocessed_image)
        logger.info(f"Completed OCR analysis, detected {len(ocr_result.text_blocks)} text blocks")
        
        # Step 4: Format the raw OCR results
        ocr_data = format_text_blocks(ocr_result)
        
        # Step 5: Generate a signed URL for the original image
        image_url = generate_signed_url(bucket_name, blob_name, expiration_seconds=86400)  # 24 hours
        
        # Step 6: Create a result dictionary with all the data
        result = {
            'image_info': {
                'bucket': bucket_name,
                'name': blob_name,
                'url': image_url,
                'content_type': content_type
            },
            'ocr_result': ocr_data,
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Successfully processed receipt image {blob_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing receipt image {blob_name}: {e}")
        raise

def get_raw_text(bucket_name: str, blob_name: str) -> Dict[str, Any]:
    """
    Simplified function to just get the raw OCR text without additional processing.
    Useful for testing and debugging the OCR results.
    
    Args:
        bucket_name: Name of the GCS bucket
        blob_name: Name of the image blob in the bucket
        
    Returns:
        Dictionary with raw OCR text and minimal metadata
        
    Raises:
        Exception: If processing fails
    """
    try:
        logger.info(f"Getting raw OCR text for {blob_name} in bucket {bucket_name}")
        
        # Download the image
        image_bytes, _ = download_image(bucket_name, blob_name)
        
        # Preprocess for better OCR results
        preprocessed_image = enhance_for_receipt(image_bytes)
        
        # Perform OCR
        ocr_result = analyze_document(preprocessed_image)
        
        # Return just the text and basic info
        return {
            'full_text': ocr_result.full_text,
            'text_block_count': len(ocr_result.text_blocks),
            'confidence': ocr_result.confidence,
            'language': ocr_result.language
        }
        
    except Exception as e:
        logger.error(f"Error getting raw OCR text for {blob_name}: {e}")
        raise
