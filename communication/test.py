from communication.pubsub_publisher import publish_event

publish_event(
    project_id="receipt-tracking-application",  # don't change this
    topic_id="receipt-updates",                 # don't change this
    message={
        "type": "receipt_update",
        "status": "processed",
        "receipt_id": "abc123",
        # "timestamp": "2025-03-26T22:30:00Z" is added automatically in this format
    }
)