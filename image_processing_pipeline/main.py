import logging
import os
import sys
from datetime import datetime

import functions_framework
from gemini_client import parse_receipt_text
from google.cloud import firestore
from models.receipt import Receipt
from ocr.pipeline import get_raw_text
from pub.pubsub_publisher import publish_event

# Force logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='FUNCTION_LOG: %(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# List of valid image extensions to process
VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']


def save_receipt_to_firestore(user_uid, parsed_receipt, image_url, raw_text, confidence_score):
    """
    Save the processed receipt information to Firestore.
    
    Args:
        user_uid: The user's unique identifier
        parsed_receipt: Dictionary with structured receipt data from Gemini
        image_url: URL to the original receipt image
        raw_text: The raw OCR text
        confidence_score: The OCR confidence score
    
    Returns:
        The document ID of the created receipt
    """
    try:
        # Initialize Firestore client
        db = firestore.Client()
        
        # Create a new Receipt object
        receipt = Receipt(
            user_uid=user_uid,
            store_name=parsed_receipt.get('store_name'),
            store_address=parsed_receipt.get('store_address'),
            date=datetime.strptime(parsed_receipt.get('date'), '%Y-%m-%d') if parsed_receipt.get('date') else None,
            time=parsed_receipt.get('time'),
            total_amount=parsed_receipt.get('total_amount'),
            raw_text=raw_text,
            image_url=image_url,
            confidence_score=confidence_score,
            processed_at=datetime.now(),
            categories=parsed_receipt.get('categories', ["Miscellaneous"])
        )
        
        # Convert the Receipt object to a dictionary
        receipt_dict = receipt.to_dict()
        
        # Create a new document in the receipts collection
        doc_ref = db.collection('receipts').document()
        doc_ref.set(receipt_dict)
        
        logger.info(f"LOGGER INFO: Saved receipt to Firestore with ID: {doc_ref.id}")
        print(f"DIRECT PRINT: Saved receipt to Firestore with ID: {doc_ref.id}")
        print(f"DIRECT PRINT: Categories assigned: {receipt.categories}")
        
        return doc_ref.id
        
    except Exception as e:
        logger.error(f"LOGGER ERROR: Failed to save receipt to Firestore: {e}")
        print(f"DIRECT PRINT: Failed to save receipt to Firestore: {e}")
        raise


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
            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "failed",
                    "message": f"Invalid file type: {file_extension}",
                    "receipt_id": name,
                    "user_uid": None,
                }
            )
            print(f"DIRECT PRINT: Published event with status \"failed\" to Pub/Sub for non-image file: {name}")
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
            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "failed",
                    "message": "User UUID not found in path",
                    "receipt_id": name,
                    "user_uid": None,
                }
            )
            print(
                f"DIRECT PRINT: Published event with status \"failed\" to Pub/Sub for missing user UUID in path: {name}")

        print(f"DIRECT PRINT: Processing file: {name} from bucket: {bucket} for user: {user_uuid}")
        publish_event(
            project_id="receipt-tracking-application",
            topic_id="receipt-updates",
            message={
                "type": "receipt_update",
                "status": "processing",
                "message": "Beginning OCR processing",
                "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                "user_uid": user_uuid,
            }
        )
        print(f"DIRECT PRINT: Published event with status \"processing\" for OCR to Pub/Sub for file: {name}")
        # Process the receipt image
        result = get_raw_text(bucket, name)

        # Log the extracted text (for now, just for debugging)
        print(f"DIRECT PRINT: Extracted text from receipt:")
        print("-" * 50)
        print(result['full_text'][:500] + "..." if len(result['full_text']) > 500 else result['full_text'])
        print("-" * 50)
        print(f"Confidence: {result['confidence']}, Text blocks: {result['text_block_count']}")

        publish_event(
            project_id="receipt-tracking-application",
            topic_id="receipt-updates",
            message={
                "type": "receipt_update",
                "status": "processing",
                "message": "OCR processing completed",
                "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                "user_uid": user_uuid,
            }
        )
        print(
            f"DIRECT PRINT: Published event with status \"processing\" for finishing OCR processing to Pub/Sub for file: {name}")

        # Use Gemini API to extract structured information from the OCR text
        if result['full_text']:
            print("DIRECT PRINT: Sending text to Gemini API for processing...")

            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "processing",
                    "message": "Gemini processing started",
                    "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                    "user_uid": user_uuid,
                }
            )
            print(
                f"DIRECT PRINT: Published event with status \"processing\" for Gemini processing to Pub/Sub for file: {name}")

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

            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "processing",
                    "message": "Gemini processing completed",
                    "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                    "user_uid": user_uuid,
                }
            )
            print(
                f"DIRECT PRINT: Published event with status \"processing\" for completing Gemini processing to Pub/Sub for file: {name}")

            try:
                total_amount = float(parsed_receipt.get("total_amount")) if parsed_receipt.get(
                    "total_amount") is not None else None
            except Exception as conv_err:
                logger.warning(f"Could not convert total_amount to float: {conv_err}")
                total_amount = None

            url = f"https://storage.cloud.google.com/receipt-photos-for-receipt-tracking-application/{name}"

            # Save the receipt to Firestore
            doc_id = save_receipt_to_firestore(
                user_uid=user_uuid,
                parsed_receipt=parsed_receipt,
                image_url=url,
                raw_text=result['full_text'],
                confidence_score=result['confidence']
            )

            print(f"DIRECT PRINT: Receipt saved with document ID: {doc_id}")
            logger.info(f"LOGGER INFO: Receipt saved with document ID: {doc_id}")

            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "success",
                    "message": "Receipt processed successfully",
                    "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                    "user_uid": user_uuid,
                }
            )
            print(f"DIRECT PRINT: Published event with status \"success\" to Pub/Sub for file: {name}")

        else:
            logger.warning("LOGGER WARNING: No text was extracted from the image, skipping Gemini processing")
            publish_event(
                project_id="receipt-tracking-application",
                topic_id="receipt-updates",
                message={
                    "type": "receipt_update",
                    "status": "failed",
                    "message": "No text extracted from image, Gemini processing skipped",
                    "receipt_id": path_parts[1] if len(path_parts) > 1 else name,
                    "user_uid": user_uuid,
                }
            )
            print(
                f"DIRECT PRINT: Published event with status \"failed\" because no text was extracted from the file to Pub/Sub for file: {name}")

        # Add user UUID to the result
        if user_uuid:
            result['user_uuid'] = user_uuid

        # Return explicit response
        return f"Successfully processed {name} with {result['text_block_count']} text blocks for user: {user_uuid}"
    except Exception as e:
        logger.error(f"LOGGER ERROR: Function execution failed: {e}")
        print(f"DIRECT PRINT: Function execution failed: {e}")
        publish_event(
            project_id="receipt-tracking-application",
            topic_id="receipt-updates",
            message={
                "type": "receipt_update",
                "status": "failed",
                "message": str(e),
                "receipt_id": cloud_event.data["name"].split('/')[1] if '/' in cloud_event.data["name"] else
                cloud_event.data["name"],
                "user_uid": cloud_event.data["name"].split('/')[0] if '/' in cloud_event.data["name"] else None,
            }
        )
        print(f"DIRECT PRINT: Published event with status \"failed\" to Pub/Sub for file: {cloud_event.data['name']}")
        raise e
