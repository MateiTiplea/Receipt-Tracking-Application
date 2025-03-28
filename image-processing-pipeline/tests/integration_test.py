import os
import time

import pytest
from google.cloud import storage

# Constants
BUCKET_NAME = "receipt-photos-for-receipt-tracking-application"
TEST_FILE_PATH = "receipt_01.jpg"
TEST_DESTINATION_PATH = f"test/test_receipt_{int(time.time())}.jpg"

def upload_test_file():
    """
    Uploads a test file to the Cloud Storage bucket to trigger the Cloud Function.
    
    Before running this test, make sure:
    1. You have a test_receipt.jpg file in the current directory
    2. You have authenticated with gcloud (gcloud auth login)
    3. You have set the proper project (gcloud config set project YOUR_PROJECT_ID)
    """
    # Check if the test file exists
    if not os.path.exists(TEST_FILE_PATH):
        raise FileNotFoundError(f"Test file {TEST_FILE_PATH} not found")
    
    # Create a storage client
    storage_client = storage.Client()
    
    # Get the bucket
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Create a new blob and upload the file
    blob = bucket.blob(TEST_DESTINATION_PATH)
    
    # Upload the file
    blob.upload_from_filename(TEST_FILE_PATH)
    
    print(f"File {TEST_FILE_PATH} uploaded to {TEST_DESTINATION_PATH}")
    
    # Wait a bit for the function to be triggered
    time.sleep(5)
    
    # Check if the file exists in the bucket
    assert blob.exists()
    
    return blob

def test_cloud_function_trigger():
    """
    Integration test for the Cloud Function.
    This test uploads a file to the bucket and verifies it exists.
    The function logs can be checked in the Google Cloud Console.
    """
    # Upload the test file
    blob = upload_test_file()
    
    # Verify the file uploaded successfully
    assert blob.exists()
    
    # Here you would typically verify the function ran successfully
    # This could be checking logs, checking a destination system, etc.
    # For this initial setup, we just verify the upload succeeded
    
    print("Test completed. Check the Google Cloud Console for function logs.")

if __name__ == "__main__":
    test_cloud_function_trigger()