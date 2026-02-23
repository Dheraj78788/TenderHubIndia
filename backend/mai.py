import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Local imports
from models.tender import TenderResponse, User
from scrapers.scraper import scrape_tenderhub
from firebase.auth import get_current_user
from firebase.db import tenders_ref, users_ref, subscriptions_ref

load_dotenv()
app = FastAPI(title="🏛️ TenderHub India API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

class ScrapeRequest(BaseModel):
    run_scraper: bool = False

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Professional government-style dashboard"""
    return HTMLResponse(open("static/index.html").read())

@app.post("/api/scrape")
async def trigger_scrape(request: ScrapeRequest):
    """Trigger scraper (limited version)"""
    if request.run_scraper:
        data = await scrape_tenderhub()
        return {"status": "Scraping completed", "sites": len(data)}
    return {"status": "Scraper ready"}

@app.get("/api/tenders")
async def get_tenders(user: User = Depends(get_current_user)):
    """Get tenders - Premium users get full details"""
    snapshot = tenders_ref.order_by_child('timestamp').limit_to_last(1).get()
    if not snapshot: 
        raise HTTPException(404, "No tender data available")
    
    latest_data = list(snapshot.values())[0]
    tenders = []
    
    for site in latest_data:
        for org in site['data']:
            for tender in org['tenders']:
                response = {
                    "site": site['site'],
                    "organisation": org['organisation'],
                    "basic": tender
                }
                # Premium users get full details
                if user.is_premium:
                    response["details"] = "Full tender details available"
                tenders.append(response)
    
    return {"tenders": tenders[:100], "total": len(tenders), "is_premium": user.is_premium}

@app.post("/api/subscribe")
async def subscribe(user: User = Depends(get_current_user)):
    """Create premium subscription"""
    subscriptions_ref.child(user.uid).update({
        "is_premium": True,
        "subscription_end": "2026-12-31",
        "subscribed_at": datetime.now().isoformat()
    })
    users_ref.child(user.uid).update({"is_premium": True})
    return {"status": "Premium activated!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
