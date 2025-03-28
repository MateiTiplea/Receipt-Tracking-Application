# Receipt Processing Cloud Function

This Cloud Function is triggered when a new receipt image is uploaded to the Google Cloud Storage bucket and will eventually process the image using OCR and AI.

## Local Development Setup

### Prerequisites

- Python 3.10 or higher
- Google Cloud SDK
- Access to the project's Google Cloud resources

### Setup

1. Clone the repository and navigate to this directory
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Testing Locally

1. Start the functions framework:
   ```
   functions-framework --target=process_receipt --signature-type=event
   ```

2. In another terminal, run the test script:
   ```
   python test_local.py
   ```

This will simulate a Cloud Storage event and test your function locally.

### Deployment

To deploy the function to Google Cloud:

```
chmod +x deploy.sh
./deploy.sh
```

## Structure

- `main.py` - Contains the Cloud Function code
- `requirements.txt` - Dependencies
- `test_local.py` - Helper script for local testing
- `deploy.sh` - Deployment script

## Function Flow

Currently, the function:
1. Gets triggered when a file is uploaded to the Cloud Storage bucket
2. Logs information about the uploaded file
3. Retrieves basic metadata about the file

Future enhancements will include:
1. OCR processing using Vision API
2. Data cleaning with Gemini AI
3. Storing structured data in Firestore
4. Publishing notifications to Pub/Sub