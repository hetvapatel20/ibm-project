from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True)
    issue_type = Column(String, index=True)      
    location = Column(String)                    
    device_id = Column(String, index=True)       
    
    severity = Column(String)                    
    status = Column(String, default="open")      
    
    assigned_engineer = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)