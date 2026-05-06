import asyncio
import random
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models

async def start_monitoring():
    print("🚦 SmartCity Monitoring System Started... (Optimized Mode)")
    
    while True:
        # 🔥 SPAM FIX: Ab loop har 10s ki jagah 60s rukk kar chalega 🔥
        await asyncio.sleep(60) 
        
        # 🔥 REDUCED CHANCE: Sirf 5% chance hai camera offline hone ka 🔥
        if random.random() < 0.05:
            faulty_device = f"CAM-{random.randint(100, 999)}"
            print(f"⚠️ ALERT: Monitoring detected failure at {faulty_device}!")
            
            # Direct database insertion
            db: Session = SessionLocal()
            try:
                new_ticket = models.Ticket(
                    issue_type="Camera Offline / Connection Lost",
                    location="Highway Node",
                    device_id=faulty_device,
                    severity="high"
                )
                db.add(new_ticket)
                db.commit()
                print(f"✅ Auto-Ticket Generated for {faulty_device}")
            except Exception as e:
                print(f"❌ Failed to auto-generate ticket: {e}")
            finally:
                db.close()