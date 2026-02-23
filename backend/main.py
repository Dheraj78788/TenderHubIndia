import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# SAFE imports with error handling
try:
    from firebase.config import tenders_ref, users_ref, subscriptions_ref, firebase_config
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase not available - using mock data")

try:
    from scrapers.scraper import scrape_tenderhub
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("⚠️ Scraper not available")

# Load environment
load_dotenv()

# FastAPI app
app = FastAPI(title="🏛️ TenderHub India API", version="1.0.0")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic Models (defined locally - no imports needed)
class ScrapeRequest(BaseModel):
    run_scraper: bool = False

class User(BaseModel):
    uid: str
    email: str
    is_premium: bool = False
    subscription_end: Optional[datetime] = None

# Security
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials=Depends(security)) -> User:
    """Mock user for now - Firebase auth later"""
    return User(uid="demo_user", email="demo@tenderhub.in", is_premium=False)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home():
    """Government-style landing page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🏛️ TenderHub India</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <div class="max-w-6xl mx-auto px-4 py-12">
            <div class="text-center mb-16">
                <div class="w-24 h-24 bg-blue-800 rounded-2xl mx-auto mb-8 flex items-center justify-center">
                    <span class="text-3xl font-bold text-white">🏛️</span>
                </div>
                <h1 class="text-5xl font-bold bg-gradient-to-r from-gray-900 to-blue-900 bg-clip-text text-transparent mb-6">
                    TenderHub India
                </h1>
                <p class="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
                    All Government Tenders - One Platform. 135+ eProcurement Portals Aggregated.
                </p>
                <div class="space-x-4">
                    <a href="/ui" class="bg-blue-600 text-white px-12 py-4 rounded-2xl font-bold text-xl hover:bg-blue-700 shadow-xl">📊 Dashboard</a>
                    <a href="/docs" class="bg-green-600 text-white px-12 py-4 rounded-2xl font-bold text-xl hover:bg-green-700 shadow-xl">📚 API Docs</a>
                </div>
            </div>
            
            <div class="grid md:grid-cols-3 gap-8 mt-24">
                <div class="bg-white p-8 rounded-3xl shadow-2xl border border-blue-100">
                    <div class="text-4xl font-bold text-blue-600 mb-4">8+</div>
                    <div class="text-gray-700 font-semibold">Portals Scraped</div>
                </div>
                <div class="bg-white p-8 rounded-3xl shadow-2xl border border-green-100">
                    <div class="text-4xl font-bold text-green-600 mb-4" id="tenders-count">1,247</div>
                    <div class="text-gray-700 font-semibold">Live Tenders</div>
                </div>
                <div class="bg-white p-8 rounded-3xl shadow-2xl border border-purple-100">
                    <div class="text-4xl font-bold text-purple-600 mb-4">24/7</div>
                    <div class="text-gray-700 font-semibold">Auto Updates</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html_content)

@app.get("/ui", response_class=HTMLResponse)
async def dashboard():
    """Professional dashboard"""
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("""
    <h1 class="text-4xl font-bold text-center mt-20 text-gray-800">📊 TenderHub Dashboard</h1>
    <p class="text-center mt-4 text-gray-600">static/index.html ready - add your professional UI here!</p>
    <div class="text-center mt-8">
        <a href="/api/tenders" class="bg-blue-600 text-white px-8 py-3 rounded-xl font-bold">🔍 View Sample Tenders</a>
    </div>
    """)

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "firebase": FIREBASE_AVAILABLE,
        "scraper": SCRAPER_AVAILABLE,
        "message": "TenderHub India API v1.0 ✅"
    }

@app.get("/api/tenders")
async def get_tenders(user: User = Depends(get_current_user)):
    """Get mock tenders (Firebase-ready)"""
    # Mock data for now
    mock_tenders = [
        {
            "site": "eProcure India", 
            "organisation": "Ministry of Defence",
            "basic": {
                "s_no": 1,
                "published_date": "23-Feb-2026",
                "closing_date": "15-Mar-2026",
                "title_and_ref": "Supply of Medical Equipment - Ref: DEF/2026/001",
                "is_premium": True
            }
        },
        {
            "site": "Maharashtra", 
            "organisation": "PWD Maharashtra",
            "basic": {
                "s_no": 2,
                "published_date": "22-Feb-2026", 
                "closing_date": "10-Mar-2026",
                "title_and_ref": "Road Construction - NH48 - Ref: PWD/2026/045",
                "is_premium": True
            }
        }
    ]
    
    return {
        "tenders": mock_tenders,
        "total": 2,
        "is_premium": user.is_premium,
        "message": "Premium users get full details + Tender IDs"
    }

@app.post("/api/scrape")
async def trigger_scrape(request: ScrapeRequest):
    """Safe scraper endpoint"""
    if not SCRAPER_AVAILABLE:
        return {"status": "Scraper not ready", "error": "scrapers/scraper.py missing"}
    
    if request.run_scraper:
        try:
            data = await scrape_tenderhub()
            return {"status": "Scraping completed", "sites": len(data)}
        except Exception as e:
            raise HTTPException(500, f"Scraping failed: {str(e)}")
    return {"status": "Scraper ready"}

@app.post("/api/subscribe")
async def subscribe(user: User = Depends(get_current_user)):
    """Mock subscription (Firebase-ready)"""
    if FIREBASE_AVAILABLE:
        try:
            subscriptions_ref.child(user.uid).update({
                "is_premium": True,
                "subscription_end": "2026-12-31",
                "subscribed_at": datetime.now().isoformat()
            })
            return {"status": "Premium activated! 🎉"}
        except Exception as e:
            raise HTTPException(500, f"Subscription failed: {str(e)}")
    return {"status": "Premium activated (demo mode)"}

if __name__ == "__main__":
    # Windows-compatible server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,  # Fixed Windows multiprocessing issue
        log_level="info"
    )
