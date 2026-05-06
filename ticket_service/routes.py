from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from typing import List
from datetime import datetime

from . import models, schemas
from .database import get_db, engine_supabase, engine_neon

router = APIRouter()

# Dono cloud databases ke liye alag session banaye hain
SupaSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_supabase) if engine_supabase else None
NeonSession = sessionmaker(autocommit=False, autoflush=False, bind=engine_neon) if engine_neon else None

@router.post("/tickets/", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    # 1. LOCAL WRITE (Hamesha pehle chalega)
    db_ticket = models.Ticket(**ticket.model_dump())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    print(f"✅ Ticket {db_ticket.ticket_id} created LOCALLY.")

    # 2. SUPABASE WRITE (Cloud 1 - Optional)
    if SupaSession:
        try:
            cloud_db = SupaSession()
            cloud_ticket = models.Ticket(**ticket.model_dump())
            cloud_ticket.ticket_id = db_ticket.ticket_id 
            cloud_db.add(cloud_ticket)
            cloud_db.commit()
            cloud_db.close()
            print("☁️ Ticket synced to SUPABASE!")
        except Exception as e:
            print(f"⚠️ Supabase Sync Failed: {e}")

    # 3. NEON WRITE (Cloud 2 - Optional)
    if NeonSession:
        try:
            neon_db = NeonSession()
            neon_ticket = models.Ticket(**ticket.model_dump())
            neon_ticket.ticket_id = db_ticket.ticket_id 
            neon_db.add(neon_ticket)
            neon_db.commit()
            neon_db.close()
            print("🌩️ Ticket synced to NEON DB!")
        except Exception as e:
            print(f"⚠️ Neon Sync Failed: {e}")

    return db_ticket

@router.get("/tickets/", response_model=List[schemas.TicketResponse])
def get_all_tickets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Ticket).offset(skip).limit(limit).all()

@router.get("/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# 🔥 ASSIGN TICKET ROUTE 🔥
@router.put("/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: int, engineer_name: str, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.assigned_engineer = engineer_name
    ticket.status = "in_progress"
    db.commit()
    return {"message": f"Ticket {ticket_id} assigned to {engineer_name}"}

# 🔥 CLOSE/RESOLVE TICKET ROUTE 🔥
@router.put("/tickets/{ticket_id}/close")
def close_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = "resolved"
    ticket.resolved_at = datetime.utcnow()
    db.commit()
    return {"message": f"Ticket {ticket_id} marked as resolved"}

# 🔥 DELETE TICKET ROUTE 🔥
@router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    db.delete(ticket)
    db.commit()
    return {"message": f"Ticket {ticket_id} permanently deleted from API."}