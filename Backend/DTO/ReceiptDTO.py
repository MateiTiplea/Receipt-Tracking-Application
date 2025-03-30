from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReceiptDTO(BaseModel):
    user_uid: Optional[str] = Field(None, example="123456")
    store_name: Optional[str] = Field(None, example="Mega Image")
    store_address: Optional[str] = Field(None, example="Strada Exemplu 123")
    date: Optional[datetime] = Field(None, example="2025-03-28T10:00:00")
    time: Optional[str] = Field(None, example="10:00")
    total_amount: Optional[float] = Field(None, example=123.45)
    raw_text: Optional[str] = Field(None, example="TOTAL: 123.45 RON")
    image_url: Optional[str] = Field(None, example="https://example.com/image.jpg")
    confidence_score: Optional[float] = Field(None, example=0.95)
    categories: Optional[List[str]] = Field(None, example=["Groceries", "Food"])  # 🔥 Nou!
    #processed_at: Optional[datetime] = Field(None, example="2025-03-28T10:05:00")
