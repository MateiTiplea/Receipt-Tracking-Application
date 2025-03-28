from fastapi import APIRouter, HTTPException
from Backend.services.receipt_service import ReceiptService
from Backend.DTO.ReceiptDTO import ReceiptDTO

receipt_router = APIRouter(prefix="/api/v1/receipts",tags=["Receipts"])

@receipt_router.post("/create-receipt")
async def create_receipt(receipt_data: ReceiptDTO):
    receipt_id = ReceiptService.create(receipt_data.dict())
    return {"message": "Receipt created", "id": receipt_id}

@receipt_router.get("/get-receipt-by/{receipt_id}")
async def get_receipt(receipt_id: str):
    receipt = ReceiptService.get(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt

@receipt_router.get("/get-receipts")
async def list_receipts():
    return ReceiptService.list()

@receipt_router.delete("/delete-receipt/{receipt_id}")
async def delete_receipt(receipt_id: str):
    ReceiptService.delete(receipt_id)
    return {"message": "Receipt deleted"}
