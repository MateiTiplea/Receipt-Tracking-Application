"""
Basic parser for OCR text extracted from images.
Provides functionality for initial text cleanup and basic OCR result handling.
"""

import logging
import re
from typing import Any, Dict

from ocr.vision_client import OcrResult

# Set up logger
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Basic text cleanup for OCR results.
    
    Args:
        text: Raw OCR text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', text)
    
    # Remove non-printable characters
    cleaned = ''.join(c for c in cleaned if c.isprintable() or c.isspace())
    
    return cleaned.strip()

def format_text_blocks(ocr_result: OcrResult) -> Dict[str, Any]:
    """
    Format OCR result into a structured dictionary for further processing.
    This is a minimal version that just organizes the raw output.
    
    Args:
        ocr_result: OCR result from Vision API
        
    Returns:
        Dictionary with formatted OCR information
    """
    try:
        # Create a simple dictionary with the raw OCR data
        ocr_data = {
            'full_text': ocr_result.full_text,
            'confidence': ocr_result.confidence,
            'language': ocr_result.language,
            'text_block_count': len(ocr_result.text_blocks),
            'text_blocks': [
                {
                    'text': block.text,
                    'confidence': block.confidence,
                    'position': {
                        'top_left': block.bounding_box.top_left,
                        'bottom_right': block.bounding_box.bottom_right
                    }
                }
                for block in ocr_result.text_blocks
            ]
        }
        
        logger.info(f"Formatted OCR result with {len(ocr_result.text_blocks)} text blocks")
        return ocr_data
        
    except Exception as e:
        logger.error(f"Error formatting OCR result: {e}")
        # Return a minimal dictionary with the raw text on error
        return {
            'full_text': ocr_result.full_text if ocr_result else "",
            'error': str(e)
        }