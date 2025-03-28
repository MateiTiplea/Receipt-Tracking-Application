import json
import time
from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class CloudEvent:
    data: Dict[str, Any]
    
def simulate_cloud_storage_event(bucket_name: str, file_name: str) -> CloudEvent:
    """
    Create a simulated Cloud Storage event for local testing.
    
    Args:
        bucket_name: The name of the bucket where the file was uploaded
        file_name: The name of the file that was uploaded
        
    Returns:
        A CloudEvent object that mimics the real Cloud Storage trigger event
    """
    event_data = {
        "bucket": bucket_name,
        "name": file_name,
        "metageneration": "1",
        "timeCreated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    
    return CloudEvent(data=event_data)

def test_function_locally():
    """
    Tests the Cloud Function locally by simulating a storage event.
    To run this test:
    1. Start the functions framework in one terminal:
       $ functions-framework --target=process_receipt --signature-type=event
    2. Run this script in another terminal:
       $ python test_local.py
    """
    bucket_name = "receipt-photos-for-receipt-tracking-application"
    file_name = "test/sample_receipt.jpg"
    
    # Create the test event
    test_event = {
        "bucket": bucket_name,
        "name": file_name,
        "metageneration": "1",
        "timeCreated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    
    cloud_event = {
        "specversion": "1.0",
        "type": "google.cloud.storage.object.v1.finalized",
        "source": f"//storage.googleapis.com/projects/_/buckets/{bucket_name}",
        "id": "1234567890",
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "datacontenttype": "application/json",
        "data": test_event
    }
    
    # Send the event to the local server
    response = requests.post(
        "http://localhost:8080",
        json=cloud_event,
        headers={"Content-Type": "application/cloudevents+json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_function_locally()