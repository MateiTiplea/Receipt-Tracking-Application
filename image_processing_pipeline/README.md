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

### Deployment

To deploy the function to Google Cloud:

```
chmod +x deploy.sh
./deploy.sh
```

Or from a powershell terminal:

```
.\deploy.ps1
```

## Function Flow

Currently, the function:
1. Gets triggered when a file is uploaded to the Cloud Storage bucket
2. Logs information about the uploaded file
3. Retrieves basic metadata about the file
4. OCR processing using Vision API

Future enhancements will include:
1. Data cleaning with Gemini AI
2. Storing structured data in Firestore
3. Publishing notifications to Pub/Sub