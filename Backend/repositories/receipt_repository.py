from google.cloud import firestore
from Backend.models.receipt import Receipt

db = firestore.Client()
collection_name = "receipts"

class ReceiptRepository:
    @staticmethod
    def create_receipt(receipt: Receipt):
        doc_ref = db.collection(collection_name).document()
        receipt.processed_at = receipt.processed_at or firestore.SERVER_TIMESTAMP
        doc_ref.set(receipt.to_dict())
        return doc_ref.id

    @staticmethod
    def get_receipt(receipt_id: str):
        doc = db.collection(collection_name).document(receipt_id).get()
        if doc.exists:
            data = doc.to_dict()
            return { "id": doc.id, **data }
        return None

    @staticmethod
    def delete_receipt(receipt_id: str):
        db.collection(collection_name).document(receipt_id).delete()

    @staticmethod
    def list_receipts():
        docs = db.collection(collection_name).stream()
        return [{ "id": doc.id, **doc.to_dict() } for doc in docs]

    @staticmethod
    def get_receipt_by_user(user_uid: str):
        docs = db.collection(collection_name).where("user_uid", "==", user_uid).stream()
        return [{ "id": doc.id, **doc.to_dict() } for doc in docs]
