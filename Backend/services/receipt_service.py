from Backend.repositories.receipt_repository import ReceiptRepository
from Backend.models.receipt import Receipt
from datetime import datetime

class ReceiptService:
    @staticmethod
    def create(receipt_data: dict):
        receipt_data['processed_at'] = datetime.utcnow()
        receipt = Receipt(**receipt_data)
        return ReceiptRepository.create_receipt(receipt)

    @staticmethod
    def get(receipt_id: str):
        return ReceiptRepository.get_receipt(receipt_id)

    @staticmethod
    def delete(receipt_id: str):
        ReceiptRepository.delete_receipt(receipt_id)

    @staticmethod
    def list():
        return ReceiptRepository.list_receipts()
