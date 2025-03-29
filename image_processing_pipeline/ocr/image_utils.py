"""
Utility functions for image preprocessing before OCR.
"""

import io
import logging
from typing import Optional, Tuple

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# Set up logger
logger = logging.getLogger(__name__)

def preprocess_image(image_bytes: bytes, resize: bool = True) -> bytes:
    """
    Preprocess an image to improve OCR results.
    
    Args:
        image_bytes: Raw image data
        resize: Whether to resize large images
        
    Returns:
        Processed image bytes
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Load image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to RGB (handles RGBA, CMYK, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize large images to improve OCR performance
            if resize and (img.width > 2000 or img.height > 2000):
                # Calculate new dimensions while maintaining aspect ratio
                ratio = min(2000 / img.width, 2000 / img.height)
                new_width = int(img.width * ratio)
                new_height = int(img.height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
                logger.info(f"Resized image from {img.width}x{img.height} to {new_width}x{new_height}")
            
            # Apply basic enhancement
            # Increase contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
            
            # Increase sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.5)
            
            # Save processed image to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            buffer.seek(0)
            
            logger.info("Successfully preprocessed image")
            return buffer.read()
            
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise

def enhance_for_receipt(image_bytes: bytes) -> bytes:
    """
    Apply specialized enhancements for receipt images.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        Processed image bytes optimized for receipt OCR
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Load image from bytes
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Convert to grayscale
            img = ImageOps.grayscale(img)
            
            # Increase contrast significantly for receipts
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.7)
            
            # Apply slight blur to remove noise
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Apply sharpening to enhance text
            img = img.filter(ImageFilter.SHARPEN)
            
            # Save processed image to bytes
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            buffer.seek(0)
            
            logger.info("Successfully enhanced image for receipt recognition")
            return buffer.read()
            
    except Exception as e:
        logger.error(f"Error enhancing image for receipt: {e}")
        raise

def crop_receipt(image_bytes: bytes) -> Tuple[bytes, bool]:
    """
    Attempt to detect and crop to just the receipt area.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        Tuple of (processed image bytes, success flag)
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # This is a simplified implementation
        # A full implementation would use edge detection and contour finding
        
        # For now, we'll just do basic preprocessing
        enhanced_image = enhance_for_receipt(image_bytes)
        
        # Return the enhanced image with a success flag of False
        # indicating that we didn't actually crop to the receipt
        return enhanced_image, False
            
    except Exception as e:
        logger.error(f"Error cropping receipt: {e}")
        # Return original image on failure
        return image_bytes, False

def detect_image_orientation(image_bytes: bytes) -> int:
    """
    Detect the orientation of an image.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        Orientation in degrees (0, 90, 180, or 270)
        
    Raises:
        Exception: If orientation detection fails
    """
    # This would normally use a more sophisticated algorithm,
    # possibly using Vision API's DOCUMENT_TEXT_DETECTION to determine
    # text orientation. For now, we'll return 0 (upright).
    return 0

def correct_orientation(image_bytes: bytes) -> bytes:
    """
    Correct the orientation of an image based on detected text orientation.
    
    Args:
        image_bytes: Raw image data
        
    Returns:
        Reoriented image bytes
        
    Raises:
        Exception: If orientation correction fails
    """
    try:
        orientation = detect_image_orientation(image_bytes)
        
        # If orientation is already upright, return original
        if orientation == 0:
            return image_bytes
        
        # Otherwise rotate the image
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Rotate according to detected orientation
            rotated = img.rotate(-orientation, expand=True)
            
            # Save rotated image to bytes
            buffer = io.BytesIO()
            rotated.save(buffer, format=img.format)
            buffer.seek(0)
            
            logger.info(f"Corrected image orientation by {orientation} degrees")
            return buffer.read()
            
    except Exception as e:
        logger.error(f"Error correcting image orientation: {e}")
        # Return original on failure
        return image_bytes