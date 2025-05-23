import os
from dotenv import load_dotenv
from google.cloud import storage
from firebase_admin import credentials, firestore, initialize_app, _apps
from google.cloud import bigquery

load_dotenv()
client = bigquery.Client()

cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not _apps:
    cred = credentials.Certificate(cred_path)
    initialize_app(cred)

db = firestore.client()
storage_client = storage.Client()
