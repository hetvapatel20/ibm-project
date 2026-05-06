from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware 
import asyncio
from contextlib import asynccontextmanager

# Rate Limiter setup
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import your modules
from . import database
from .routes import router
from .monitor import start_monitoring

# 1. Limiter Setup (IP address track karne ke liye)
limiter = Limiter(key_func=get_remote_address)

# 🔥 MODERN LIFESPAN (Database + Monitor dono yahan start honge)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- DUAL DATABASE STARTUP ---
    print("⏳ Initializing Databases (Local & Cloud)...")
    database.init_db()  # Yeh function dono DB me tables aur default Admin bana dega
    
    # --- BACKGROUND MONITOR STARTUP ---
    print("🚀 Starting Background Monitor...")
    task = asyncio.create_task(start_monitoring())
    
    yield # App jab tak chalegi, yahan ruki rahegi
    
    # --- SHUTDOWN CLEANUP ---
    task.cancel()

# App initialize karna
app = FastAPI(title="SmartCity Service Desk", lifespan=lifespan)

# 2. Limiter ko App ke sath jodna aur Error Handler lagana
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 🔥 CORS FIX: Allow All Origins so UI doesn't hang 🔥
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Har IP se request allow karega
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Router include karna
app.include_router(router, prefix="/api/v1", tags=["Tickets"])

@app.get("/")
@limiter.limit("10/minute") 
def root(request: Request): # 'request' pass karna zaroori hai limiter ke liye
    return {
        "message": "SmartCity Ticket System API is Running Perfectly!", 
        "docs": "Go to /docs for API documentation."
    }