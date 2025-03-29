from communication.pubsub_publisher import publish_event

publish_event(
    project_id="receipt-tracking-application",  # don't change this
    topic_id="receipt-updates",                 # don't change this
    message={
        "type": "receipt_update",
        "status": "failed", # or success or begin_processing
        "message": "No text extracted from image, Gemini processing skipped", # optional, for failed status
        "receipt_id": "receipt_id_placeholder",  # replace with actual receipt ID
        "user_uid": "user_uid_placeholder",  # replace with actual user UID
    }
)