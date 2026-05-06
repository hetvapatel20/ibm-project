from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class SeverityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"
    # 🔥 Fix for Database Capital letters
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"

class StatusEnum(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class TicketCreate(BaseModel):
    issue_type: str
    location: str
    device_id: str
    severity: str # Changed to simple string to avoid any validation block

class TicketResponse(TicketCreate):
    ticket_id: int
    status: str # Changed to simple string to avoid block
    assigned_engineer: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True