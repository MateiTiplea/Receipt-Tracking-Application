from google.cloud import pubsub_v1
import json


def publish_event(project_id, topic_id, message: dict):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    data = json.dumps(message).encode("utf-8")
    future = publisher.publish(topic_path, data)
    print(f"Published message to {topic_id}: {message}")
    return future.result()
