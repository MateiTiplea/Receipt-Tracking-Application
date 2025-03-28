from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Receipt:
    """Represents a processed receipt."""
    store_name: Optional[str] = None
    store_address: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    total_amount: Optional[float] = None
    raw_text: Optional[str] = None
    image_url: Optional[str] = None
    confidence_score: Optional[float] = None
    processed_at: Optional[datetime] = None
    
    
    def to_dict(self):
        """Convert to dictionary for Firestore storage."""
        result = {}
        for k, v in asdict(self).items():
            if k == 'date' and v:
                result[k] = v.isoformat()
            elif k == 'processed_at' and v:
                result[k] = v.isoformat()
            elif v is not None:
                result[k] = v
        return result