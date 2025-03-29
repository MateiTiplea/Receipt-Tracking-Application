import logging
import os
import re
import sys

import functions_framework
from gemini_client import parse_receipt_text
from ocr.pipeline import get_raw_text, process_receipt_image

# Force logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='FUNCTION_LOG: %(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# List of valid image extensions to process
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

@functions_framework.cloud_event
def process_receipt(cloud_event):
    """Cloud Function triggered by Cloud Storage."""
    # Add more prominent logging
    print(f"DIRECT PRINT: Function triggered with event: {cloud_event}")
    logger.info(f"LOGGER INFO: Processing started")
    
    try:
        # Extract file information
        bucket = cloud_event.data["bucket"]
        name = cloud_event.data["name"]
        
        logger.info(f"LOGGER INFO: File {name} uploaded to {bucket}")
        
        # Skip folders (they end with a slash)
        if name.endswith('/'):
            logger.info(f"LOGGER INFO: Skipping folder: {name}")
            return f"Skipped processing for folder: {name}"
        
        # Check if file has a valid image extension
        _, file_extension = os.path.splitext(name)
        if file_extension.lower() not in VALID_IMAGE_EXTENSIONS:
            logger.info(f"LOGGER INFO: Skipping non-image file: {name} with extension {file_extension}")
            return f"Skipped processing for non-image file: {name}"
        
        # Extract user UUID from path (assuming format: {user_uuid}/image.jpg)
        path_parts = name.split('/')
        user_uuid = None
        
        if len(path_parts) >= 2:
            # The user UUID should be the parent folder
            user_uuid = path_parts[0]
            logger.info(f"LOGGER INFO: Extracted user UUID: {user_uuid} from path: {name}")
        else:
            logger.warning(f"LOGGER WARNING: Could not extract user UUID from path: {name}")
        
        print(f"DIRECT PRINT: Processing file: {name} from bucket: {bucket} for user: {user_uuid}")
        
        # Process the receipt image
        result = get_raw_text(bucket, name)
        
        # Log the extracted text (for now, just for debugging)
        print(f"DIRECT PRINT: Extracted text from receipt:")
        print("-" * 50)
        print(result['full_text'][:500] + "..." if len(result['full_text']) > 500 else result['full_text'])
        print("-" * 50)
        print(f"Confidence: {result['confidence']}, Text blocks: {result['text_block_count']}")
        
        # Use Gemini API to extract structured information from the OCR text
        if result['full_text']:
            print("DIRECT PRINT: Sending text to Gemini API for processing...")
            
            # Parse receipt text with Gemini
            parsed_receipt = parse_receipt_text(result['full_text'])
            
            # Print the structured information
            print("DIRECT PRINT: Gemini API extracted the following information:")
            print("-" * 50)
            print(f"Store Name: {parsed_receipt.get('store_name')}")
            print(f"Store Address: {parsed_receipt.get('store_address')}")
            print(f"Date: {parsed_receipt.get('date')}")
            print(f"Time: {parsed_receipt.get('time')}")
            print(f"Total Amount: {parsed_receipt.get('total_amount')}")
            print("-" * 50)
            
            # Add structured data to the result
            result['parsed_receipt'] = parsed_receipt
        else:
            logger.warning("LOGGER WARNING: No text was extracted from the image, skipping Gemini processing")
        
        # Add user UUID to the result
        if user_uuid:
            result['user_uuid'] = user_uuid
        
        # Return explicit response
        return f"Successfully processed {name} with {result['text_block_count']} text blocks for user: {user_uuid}"
    except Exception as e:
        logger.error(f"LOGGER ERROR: Function execution failed: {e}")
        raise e