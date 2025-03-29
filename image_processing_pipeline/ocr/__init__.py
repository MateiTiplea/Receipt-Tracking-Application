"""
OCR package for the receipt processing pipeline.
Provides functionality for text extraction from images using Google Cloud Vision API.
"""

from ocr.vision_client import (
    OcrResult,
    analyze_document,
    detect_text_blocks,
    extract_text,
    get_text_annotations,
)

__all__ = [
    'extract_text',
    'get_text_annotations', 
    'analyze_document',
    'detect_text_blocks',
    'OcrResult'
]