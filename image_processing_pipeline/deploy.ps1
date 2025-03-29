# PowerShell script to deploy the Cloud Function to Google Cloud

# Configuration
$PROJECT_ID = gcloud config get-value project
$REGION = "europe-west1"  # Change to your preferred region
$FUNCTION_NAME = "process_receipt"
$RUNTIME = "python310"
$BUCKET_NAME = "receipt-photos-for-receipt-tracking-application"
$ENTRY_POINT = "process_receipt"

Write-Host "Deploying Cloud Function '$FUNCTION_NAME' to project '$PROJECT_ID'..."

# Deploy the function
gcloud functions deploy $FUNCTION_NAME `
  --gen2 `
  --runtime=$RUNTIME `
  --region=$REGION `
  --source="." `
  --entry-point=$ENTRY_POINT `
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" `
  --trigger-event-filters="bucket=$BUCKET_NAME" `
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest" `
  --memory=256MB

Write-Host "Deployment completed successfully!"