"""
Google Cloud Vision API client module for OCR processing.
Handles sending images to the Vision API and parsing the responses.
"""

import io
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import vision
from google.cloud.vision_v1 import types
from google.cloud.vision_v1.types import Feature

# Set up logger
logger = logging.getLogger(__name__)

@dataclass
class BoundingBox:
    """Represents a bounding box for a text block."""
    vertices: List[Dict[str, int]] = field(default_factory=list)
    
    @property
    def top_left(self) -> Tuple[int, int]:
        """Get the top-left coordinate of the bounding box."""
        if not self.vertices or len(self.vertices) < 1:
            return (0, 0)
        return (self.vertices[0].get('x', 0), self.vertices[0].get('y', 0))
    
    @property
    def bottom_right(self) -> Tuple[int, int]:
        """Get the bottom-right coordinate of the bounding box."""
        if not self.vertices or len(self.vertices) < 3:
            return (0, 0)
        return (self.vertices[2].get('x', 0), self.vertices[2].get('y', 0))

@dataclass
class TextBlock:
    """Represents a block of text detected in an image."""
    text: str
    confidence: float
    bounding_box: BoundingBox = field(default_factory=BoundingBox)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'bounding_box': {
                'vertices': self.bounding_box.vertices
            }
        }

@dataclass
class OcrResult:
    """Represents the result of an OCR operation."""
    full_text: str
    text_blocks: List[TextBlock] = field(default_factory=list)
    language: Optional[str] = None
    orientation: Optional[str] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'full_text': self.full_text,
            'text_blocks': [block.to_dict() for block in self.text_blocks],
            'language': self.language,
            'orientation': self.orientation,
            'confidence': self.confidence
        }

class VisionClient:
    """Client for interacting with Google Cloud Vision API."""
    
    def __init__(self):
        """Initialize the Vision API client."""
        try:
            self.client = vision.ImageAnnotatorClient()
            logger.info("Vision API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Vision API client: {e}")
            raise
    
    def extract_text(self, image_bytes: bytes) -> OcrResult:
        """
        Extract text from an image using OCR.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            OcrResult object containing extracted text and metadata
            
        Raises:
            Exception: If Vision API processing fails
        """
        try:
            # Create image object
            image = vision.Image(content=image_bytes)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Extract text annotations
            text_annotations = response.text_annotations
            
            # If no text found, return empty result
            if not text_annotations:
                logger.warning("No text detected in the image")
                return OcrResult(full_text="", confidence=0.0)
            
            # The first annotation contains the entire text
            full_text = text_annotations[0].description if text_annotations else ""
            
            # Extract individual text blocks (starting from index 1)
            text_blocks = []
            for annotation in text_annotations[1:]:
                vertices = []
                for vertex in annotation.bounding_poly.vertices:
                    vertices.append({'x': vertex.x, 'y': vertex.y})
                
                block = TextBlock(
                    text=annotation.description,
                    confidence=0.0,  # Basic text_detection doesn't provide confidence scores
                    bounding_box=BoundingBox(vertices=vertices)
                )
                text_blocks.append(block)
                
            # Create the result object
            result = OcrResult(
                full_text=full_text,
                text_blocks=text_blocks,
                confidence=1.0 if text_blocks else 0.0  # No confidence score in basic text detection
            )
            
            logger.info(f"Successfully extracted text from image: {len(result.text_blocks)} blocks")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise
    
    def analyze_document(self, image_bytes: bytes) -> OcrResult:
        """
        Perform document analysis with more detailed OCR.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            OcrResult object containing extracted text and metadata
            
        Raises:
            Exception: If Vision API processing fails
        """
        try:
            # Create image object
            image = vision.Image(content=image_bytes)
            
            # Configure document text detection
            features = [Feature(type_=Feature.Type.DOCUMENT_TEXT_DETECTION)]
            request = types.AnnotateImageRequest(image=image, features=features)
            
            # Send the request
            response = self.client.annotate_image(request=request)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Process full text document
            document = response.full_text_annotation
            
            # No text detected
            if not document or not document.text:
                logger.warning("No document text detected in the image")
                return OcrResult(full_text="", confidence=0.0)
            
            # Extract text blocks
            text_blocks = []
            full_text = document.text
            
            # Language detection
            language = None
            if document.pages and document.pages[0].property and document.pages[0].property.detected_languages:
                language = document.pages[0].property.detected_languages[0].language_code
            
            # Process all blocks
            for page in document.pages:
                for block in page.blocks:
                    block_text = ""
                    confidence = block.confidence
                    
                    # Extract text from paragraphs and words
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            block_text += word_text + " "
                    
                    block_text = block_text.strip()
                    if block_text:
                        # Create bounding box
                        vertices = []
                        for vertex in block.bounding_box.vertices:
                            vertices.append({'x': vertex.x, 'y': vertex.y})
                        
                        text_block = TextBlock(
                            text=block_text,
                            confidence=confidence,
                            bounding_box=BoundingBox(vertices=vertices)
                        )
                        text_blocks.append(text_block)
            
            # Calculate average confidence
            avg_confidence = 0.0
            if text_blocks:
                avg_confidence = sum(block.confidence for block in text_blocks) / len(text_blocks)
            
            # Create result
            result = OcrResult(
                full_text=full_text,
                text_blocks=text_blocks,
                language=language,
                confidence=avg_confidence
            )
            
            logger.info(f"Successfully analyzed document: {len(result.text_blocks)} blocks, confidence: {avg_confidence:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            raise
    
    def get_text_annotations(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Get raw text annotations from Vision API.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            List of text annotation dictionaries
            
        Raises:
            Exception: If Vision API processing fails
        """
        try:
            # Create image object
            image = vision.Image(content=image_bytes)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            
            if response.error.message:
                raise Exception(f"Vision API error: {response.error.message}")
            
            # Convert annotations to dictionaries
            annotations = []
            for annotation in response.text_annotations:
                vertices = []
                for vertex in annotation.bounding_poly.vertices:
                    vertices.append({'x': vertex.x, 'y': vertex.y})
                
                anno_dict = {
                    'description': annotation.description,
                    'bounding_poly': {
                        'vertices': vertices
                    },
                    'locale': annotation.locale
                }
                annotations.append(anno_dict)
            
            return annotations
            
        except Exception as e:
            logger.error(f"Error getting text annotations: {e}")
            raise
    
    def detect_text_blocks(self, image_bytes: bytes) -> List[TextBlock]:
        """
        Detect text blocks in an image.
        
        Args:
            image_bytes: Raw image data
            
        Returns:
            List of TextBlock objects
            
        Raises:
            Exception: If Vision API processing fails
        """
        try:
            result = self.extract_text(image_bytes)
            return result.text_blocks
        except Exception as e:
            logger.error(f"Error detecting text blocks: {e}")
            raise

# Singleton instance for use throughout the application
vision_client = VisionClient()

def extract_text(image_bytes: bytes) -> OcrResult:
    """Convenience function to extract text using the singleton client."""
    return vision_client.extract_text(image_bytes)

def analyze_document(image_bytes: bytes) -> OcrResult:
    """Convenience function to analyze a document using the singleton client."""
    return vision_client.analyze_document(image_bytes)

def get_text_annotations(image_bytes: bytes) -> List[Dict[str, Any]]:
    """Convenience function to get text annotations using the singleton client."""
    return vision_client.get_text_annotations(image_bytes)

def detect_text_blocks(image_bytes: bytes) -> List[TextBlock]:
    """Convenience function to detect text blocks using the singleton client."""
    return vision_client.detect_text_blocks(image_bytes)