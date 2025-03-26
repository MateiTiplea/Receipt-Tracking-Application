from datetime import datetime, UTC

from google.cloud import pubsub_v1
import json


def publish_event(project_id, topic_id, message: dict):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    if "timestamp" not in message:
        message["timestamp"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Published message to {topic_id}: {message}")
    return future.result()
