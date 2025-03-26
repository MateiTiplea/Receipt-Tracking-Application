# 🛰️ Real-Time Messaging & Notification System

This module enables **real-time communication** between Google Cloud Pub/Sub, your backend, and connected frontend clients using WebSockets.

It allows the app to:
- **Publish events** (e.g. new receipt uploaded, processed)
- **Subscribe to events** via Pub/Sub
- **Broadcast events** in real-time to all connected WebSocket clients

---

## 📁 Project Structure

```
communication/
│
├── websocket_server.py             # Entry point: runs WebSocket server and Pub/Sub listener
├── client_manager.py               # Tracks WebSocket clients and broadcasts updates
├── pubsub_listener.py              # Subscribes to Pub/Sub and relays messages
├── pubsub_publisher.py             # Used to publish messages to Pub/Sub
├── requirements.txt                # Python dependencies
├── test.py                         # Test script to publish messages
└── websocket_test_client.html      # Test client to connect to WebSocket server

```

---

## 🔌 How It Works

### 1. Pub/Sub Flow

- Messages are published to topic `receipt-updates`
- `pubsub_listener.py` receives these messages
- Messages are then broadcasted to connected WebSocket clients

### 2. WebSocket Server

- Frontend clients connect to `ws://<server>:8765`
- They receive real-time updates about receipt processing, upload status, etc.

---

## 🚀 How to Run the WebSocket Server

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

2. **Authenticate with Google Cloud (one-time)**

```bash
gcloud auth application-default login
```

3. **Run the server**

```bash
python websocket_server.py
```

You should see:

```
Listening to Pub/Sub...
WebSocket server started on ws://localhost:8765
```

---

## 📦 Publishing Events (for Cloud Functions or Backend)

Use `publish_event` from `pubsub_publisher.py` to publish updates to Pub/Sub:

```python
from communication.pubsub_publisher import publish_event

publish_event(
    project_id="receipt-tracking-application",    # don't change this
    topic_id="receipt-updates",                   # don't change this
    message={
        "type": "receipt_update",
        "status": "processed", # or "processing_started", "failed"
        "receipt_id": "abc123"
        # "timestamp": "2025-03-26T22:30:00Z" is added automatically in this format
    }
)
```

> ✅ **Person A** should use this when a new receipt image is uploaded.
> 
> ✅ **Person B** should use this to publish status updates like `processing_started`, `processed`, `failed`.

---

## 🖥️ Testing WebSocket Client

Use this to test from your browser:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>WebSocket Test</title>
  </head>
  <body>
    <h2>WebSocket Test</h2>
    <ul id="updates"></ul>
    <script>
      const ws = new WebSocket("ws://localhost:8765");
      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        const li = document.createElement("li");
        li.textContent = `Receipt ${msg.receipt_id} → ${msg.status}`;
        document.getElementById("updates").appendChild(li);
      };
    </script>
  </body>
</html>
```

Open this in your browser and you should see updates as they come in(you have to publish something to see).

Example:

```plaintext
WebSocket Test
    
    - Receipt abc123 → processing_started
    - Receipt abc124 → processed
```
---

## 🧠 Expected Message Format

Messages published to Pub/Sub and sent to clients must follow this JSON structure:

```json
{
  "type": "receipt_update",           // or "receipt_upload"
  "status": "processing_started",     // or "received", "processed", "failed"
  "receipt_id": "abc123",
  "timestamp": "2025-03-26T22:00:00Z"
}
```

---

## 👥 Integration Notes

- **Frontend (Person C)** connects to the WebSocket and handles incoming messages.
- **Backend / Cloud Functions (Person A & B)** publish messages using `pubsub_publisher.py`
- **This module (Person D)** runs the WebSocket server + handles Pub/Sub messaging.

---

