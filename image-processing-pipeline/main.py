import logging
import sys

import functions_framework

# Force logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='FUNCTION_LOG: %(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

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
        print(f"DIRECT PRINT: Processing file: {name} from bucket: {bucket}")
        
        # Return explicit response
        return f"Successfully processed {name}"
    except Exception as e:
        logger.error(f"LOGGER ERROR: Function execution failed: {e}")
        raise e