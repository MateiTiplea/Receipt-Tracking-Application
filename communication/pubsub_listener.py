from google.cloud import pubsub_v1
import asyncio
from client_manager import broadcast


def handle_pubsub_message(message):
    print(f"Pub/Sub message: {message.data}")
    data = message.data.decode("utf-8")
    asyncio.run(broadcast(data))
    message.ack()


def start_listener(project_id, subscription_id):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)
    subscriber.subscribe(subscription_path, callback=handle_pubsub_message)
    print("Listening to Pub/Sub...")
