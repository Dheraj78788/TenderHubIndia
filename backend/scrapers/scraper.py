import asyncio
import json
import logging
import random
from datetime import datetime
from typing import List, Dict
from playwright.async_api import async_playwright, BrowserContext
from bs4 import BeautifulSoup
import asyncio_throttle
from .config import TENDER_SITES, MAX_TENDERS_PER_ORG

logger = logging.getLogger(__name__)
limiter = asyncio_throttle.limiter(MAX_CONCURRENT_TENDERS, 1)

async def scrape_tenderhub():
    """Main scraper - LIMITS to 10 tenders per org to prevent crashes"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        all_data = []
        for site in TENDER_SITES:
            site_data = await scrape_site(site, browser)
            all_data.append({"site": site["name"], "data": site_data})
            # Save progress
            await save_progress(all_data)
        
        await browser.close()
    return all_data

async def scrape_site(site: Dict, browser) -> List[Dict]:
    """Scrape single site with 10 tender limit"""
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = await context.new_page()
    
    await page.goto(site['org_url'], wait_until="domcontentloaded", timeout=60000)
    soup = BeautifulSoup(await page.content(), "html.parser")
    
    org_rows = soup.select("table#table tbody tr[id^='informal']")
    site_data = []
    
    for row in org_rows[:20]:  # Limit orgs too for demo
        org_name = row.find_all("td")[1].text.strip()
        org_link = site['base_url'] + row.find("a")["href"]
        
        tenders = await scrape_org_tenders(page, org_link, site, max_tenders=MAX_TENDERS_PER_ORG)
        if tenders:
            site_data.append({"organisation": org_name, "tenders": tenders})
    
    await context.close()
    return site_data

async def scrape_org_tenders(page, org_url: str, site: Dict, max_tenders: int = 10):
    """Get only first 10 tenders per org"""
    await page.goto(org_url, wait_until="domcontentloaded", timeout=45000)
    soup = BeautifulSoup(await page.content(), "html.parser")
    
    table = soup.find("table", id="table")
    if not table: return []
    
    rows = table.find("tbody").find_all("tr")[1:][:max_tenders]  # LIMIT 10!
    tenders = []
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6: continue
        
        title_tag = cols[4].find("a")
        tender = {
            "s_no": len(tenders) + 1,
            "published_date": cols[1].text.strip(),
            "closing_date": cols[2].text.strip(),
            "title_link": site['base_url'] + title_tag["href"] if title_tag else None,
            "title_and_ref": cols[4].text.strip(),
            "is_premium": True
        }
        tenders.append(tender)
    
    return tenders

async def save_progress(data):
    """Save to Firebase with progress tracking"""
    from backend.firebase.db import tenders_ref
    timestamp = datetime.now().isoformat()
    tenders_ref.child(timestamp).set(data)
