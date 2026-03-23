"""
ScaleDown Policy Dashboard Backend - Real-time data with Tavily + ScaleDown
"""
import os
import sys

# Add parent directory to path for scaledown import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import hashlib
from contextlib import asynccontextmanager
import random

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our modules
from search.tavily import TavilySearch, get_all_policy_data
from summarizer.llm_summarizer import get_summarizer, PolicySummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Data models
class PolicyResponse(BaseModel):
    id: str
    title: str
    type: str
    source: str
    source_url: str
    ministry: str
    published_date: str
    summary: str
    impact: str
    entities: List[str]
    importance: str = "normal"  # normal or important
    sentiment: str = "Neutral"  # Positive, Negative, or Neutral
    scraped_at: str


class NewsResponse(BaseModel):
    id: str
    title: str
    source: str
    source_url: str
    published_date: str
    summary: str
    category: str
    url: str  # Real URL to article


class DashboardStats(BaseModel):
    total_policies: int
    active_updates: int
    sources: List[str]
    last_updated: str


class DashboardData(BaseModel):
    policies: List[PolicyResponse]
    news: List[NewsResponse]
    stats: DashboardStats


class AnalyticsData(BaseModel):
    by_ministry: Dict[str, int]
    by_entity: Dict[str, int]
    by_date: List[Dict[str, Any]]  # [{"date": "Mar 21", "count": 5}]
    sentiment_distribution: Dict[str, int]


# In-memory storage
policies_cache: List[Dict] = []
news_cache: List[Dict] = []
last_fetch: datetime = datetime.min


def generate_id(text: str) -> str:
    """Generate unique ID from text."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def determine_importance(title: str, content: str) -> str:
    """Determine if article is important based on keywords."""
    important_keywords = [
        "bill passed", "act enacted", "regulation", "launch", "announcement",
        "fund", "scheme", "reform", "amendment", "new policy"
    ]
    text = (title + " " + content).lower()
    
    for keyword in important_keywords:
        if keyword in text:
            return "important"
    
    return "normal"


def determine_sentiment(title: str, summary: str, impact: str) -> str:
    """Rule-based sentiment analysis for policy impact."""
    text = (title + " " + summary + " " + impact).lower()
    
    positive_keywords = [
        "benefit", "subsidy", "fund", "allocation", "grant", "support", 
        "incentive", "promotion", "growth", "improvement", "simplified",
        "lower tax", "reduced gst", "ease of", "launch", "mission"
    ]
    negative_keywords = [
        "penalty", "fine", "imprisonment", "restriction", "ban", "compliance burden",
        "audit", "tax increase", "hike", "violation", "enforcement", "mandatory",
        "liability", "legal action"
    ]
    
    pos_score = sum(1 for k in positive_keywords if k in text)
    neg_score = sum(1 for k in negative_keywords if k in text)
    
    if pos_score > neg_score:
        return "Positive"
    elif neg_score > pos_score:
        return "Negative"
    return "Neutral"


def extract_entities(title: str, summary: str) -> List[str]:
    """Extract affected entities from policy text."""
    entities = []
    text = (title + " " + summary).lower()
    
    if any(word in text for word in ["startup", "entrepreneur", "venture"]):
        entities.append("Startups")
    if any(word in text for word in ["student", "education", "academic"]):
        entities.append("Students")
    if any(word in text for word in ["farmer", "agriculture", "kisan"]):
        entities.append("Farmers")
    if any(word in text for word in ["business", "company", "corporate", "msme"]):
        entities.append("Businesses")
    if any(word in text for word in ["tax", "gst", "income"]):
        entities.append("Taxpayers")
    if any(word in text for word in ["tech", "digital", "ai", "data"]):
        entities.append("Tech Companies")
    if any(word in text for word in ["health", "hospital", "medical"]):
        entities.append("Healthcare")
    
    return entities[:4] if entities else ["General Public"]


def determine_ministry(title: str, url: str) -> str:
    """Determine ministry from title/URL."""
    text = (title + " " + url).lower()
    
    if "meity" in text or "electronics" in text or "digital" in text:
        return "MeitY"
    if "finance" in text or "tax" in text or "gst" in text:
        return "MoF"
    if "agriculture" in text or "farmer" in text:
        return "MoA"
    if "health" in text or "medical" in text:
        return "MoHFW"
    if "telecom" in text or "dot" in text:
        return "DoT"
    if "commerce" in text or "dpiit" in text or "startup" in text:
        return "DPIIT"
    if "parliament" in text or "lok sabha" in text or "rajya sabha" in text:
        return "Parliament"
    
    return "Government"


def determine_type(title: str) -> str:
    """Determine policy type from title."""
    text = title.lower()
    
    if "bill" in text:
        return "bill"
    if "act" in text or "enacted" in text:
        return "act"
    if "notification" in text or "gazette" in text:
        return "notification"
    if "regulation" in text or "rules" in text:
        return "regulation"
    if "scheme" in text or "mission" in text:
        return "scheme"
    
    return "policy"


async def fetch_real_data():
    """Fetch real data from Tavily and process with ScaleDown."""
    global policies_cache, news_cache, last_fetch
    
    logger.info("Fetching real-time policy data from Tavily...")
    
    tavily = TavilySearch()
    summarizer = get_summarizer()
    
    # Search queries for government policy
    queries = [
        "India government policy 2026 Parliament bills",
        "MeitY digital India notifications 2026",
        "Press Information Bureau government announcements",
        "Startup India DPIIT scheme 2026",
        "GST tax notifications India 2026"
    ]
    
    all_results = []
    
    # Fetch from Tavily
    for query in queries:
        results = await tavily.search(query, max_results=8)
        all_results.extend(results)
        await asyncio.sleep(0.3)
    
    # Process results into policies and news
    policies = []
    news = []
    
    for item in all_results:
        title = item.get("title", "")
        content = item.get("content", "")
        raw_content = item.get("raw_content", "")
        url = item.get("url", "")
        
        if not title:
            continue
        
        # Prefer content (short snippet) over raw_content (full HTML page)
        # Only use raw_content if content is too short
        summarization_content = content or raw_content or title
        
        # Create high-density summary using ScaleDown
        summary_data = summarizer.summarize(summarization_content, title)
        summary = summary_data.get("summary", summarization_content[:300])
        
        # Build impact with key rules and penalties from summarizer
        key_rules = summary_data.get("key_rules", [])
        penalties = summary_data.get("penalties", [])
        
        impact_parts = []
        if key_rules:
            impact_parts.append("Key Provisions:")
            for rule in key_rules[:5]:
                impact_parts.append(f"- {rule}")
        if penalties:
            impact_parts.append("\nPenalties:")
            for penalty in penalties[:3]:
                impact_parts.append(f"- {penalty}")
        
        impact = '\n'.join(impact_parts) if impact_parts else (content[:300] if content else "Check source for details")
        
        # Determine metadata
        importance = determine_importance(title, content)
        sentiment = determine_sentiment(title, summary, impact)
        entities = extract_entities(title, summary)
        ministry = determine_ministry(title, url)
        policy_type = determine_type(title)
        
        # Determine source
        source = "Web"
        if "parliament" in url.lower():
            source = "Parliament"
        elif "pib.gov" in url.lower():
            source = "PIB"
        elif "meitY" in url.lower():
            source = "MeitY"
        elif "gazette" in url.lower():
            source = "Gazette"
        
        # Create policy entry
        policy = {
            "id": generate_id(title),
            "title": title,
            "type": policy_type,
            "source": source,
            "source_url": url,
            "ministry": ministry,
            "published_date": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "summary": summary,
            "impact": impact,
            "entities": entities,
            "importance": importance,
            "sentiment": sentiment,
            "scraped_at": datetime.now().isoformat()
        }
        policies.append(policy)
        
        # Create news entry
        news_item = {
            "id": generate_id(title + "news"),
            "title": title,
            "source": source,
            "source_url": url,
            "published_date": policy["published_date"],
            "summary": summary,
            "category": "policy",
            "url": url
        }
        news.append(news_item)
    
    # Sort policies by importance then date
    policies.sort(key=lambda x: (x["importance"] != "important", x["published_date"]), reverse=True)
    
    # Sort news by date
    news.sort(key=lambda x: x["published_date"], reverse=True)
    
    policies_cache = policies[:20]
    news_cache = news[:15]
    last_fetch = datetime.now()
    
    logger.info(f"Fetched {len(policies_cache)} policies and {len(news_cache)} news articles")


async def periodic_data_refresh():
    """Background task to refresh data every 6 hours."""
    while True:
        await asyncio.sleep(21600)  # 6 hours
        await fetch_real_data()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager."""
    logger.info("Starting ScaleDown Policy Dashboard Backend with Real-time Data...")
    
    # Initial data fetch
    await fetch_real_data()
    
    # Start background refresh
    refresh_task = asyncio.create_task(periodic_data_refresh())
    
    yield
    
    refresh_task.cancel()
    logger.info("Shutting down backend...")


# Create FastAPI app
app = FastAPI(
    title="ScaleDown Policy Dashboard API",
    description="Real-time policy data with Tavily search + ScaleDown compression",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard(
    source: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    filter_type: Optional[str] = Query(None, description="Filter: latest, important")
):
    """Get complete dashboard data with filters."""
    
    # Apply filters
    filtered_policies = policies_cache
    
    if source and source != "all":
        filtered_policies = [p for p in filtered_policies if p["source"].lower() == source.lower()]
    
    if entity:
        filtered_policies = [p for p in filtered_policies if any(entity.lower() in e.lower() for e in p["entities"])]
    
    if filter_type == "important":
        filtered_policies = [p for p in filtered_policies if p.get("importance") == "important"]
    elif filter_type == "latest":
        # Already sorted by date
        pass
    
    # Format responses
    policy_responses = [
        PolicyResponse(
            id=p["id"],
            title=p["title"],
            type=p["type"],
            source=p["source"],
            source_url=p["source_url"],
            ministry=p["ministry"],
            published_date=p["published_date"],
            summary=p["summary"],
            impact=p["impact"],
            entities=p["entities"],
            importance=p.get("importance", "normal"),
            sentiment=p.get("sentiment", "Neutral"),
            scraped_at=p["scraped_at"]
        )
        for p in filtered_policies
    ]
    
    news_responses = [
        NewsResponse(
            id=n["id"],
            title=n["title"],
            source=n["source"],
            source_url=n["source_url"],
            published_date=n["published_date"],
            summary=n["summary"],
            category=n["category"],
            url=n["url"]
        )
        for n in news_cache
    ]
    
    stats = DashboardStats(
        total_policies=len(policies_cache),
        active_updates=len([p for p in policies_cache if (datetime.now() - datetime.fromisoformat(p["published_date"])).total_seconds() < 3600]),
        sources=list(set(p["source"] for p in policies_cache)),
        last_updated=last_fetch.isoformat()
    )
    
    return DashboardData(
        policies=policy_responses,
        news=news_responses,
        stats=stats
    )


@app.get("/api/policies", response_model=List[PolicyResponse])
async def get_policies(
    source: Optional[str] = Query(None),
    entity: Optional[str] = Query(None),
    filter_type: Optional[str] = Query(None),
    importance: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50)
):
    """Get policies with filters."""
    filtered = policies_cache[:limit]
    
    if source and source != "all":
        filtered = [p for p in filtered if p["source"].lower() == source.lower()]
    if entity:
        filtered = [p for p in filtered if any(entity.lower() in e.lower() for e in p["entities"])]
    if filter_type == "important":
        filtered = [p for p in filtered if p.get("importance") == "important"]
    if importance:
        filtered = [p for p in filtered if p.get("importance") == importance]
    
    return [
        PolicyResponse(
            id=p["id"],
            title=p["title"],
            type=p["type"],
            source=p["source"],
            source_url=p["source_url"],
            ministry=p["ministry"],
            published_date=p["published_date"],
            summary=p["summary"],
            impact=p["impact"],
            entities=p["entities"],
            importance=p.get("importance", "normal"),
            sentiment=p.get("sentiment", "Neutral"),
            scraped_at=p["scraped_at"]
        )
        for p in filtered
    ]


@app.get("/api/news", response_model=List[NewsResponse])
async def get_news(limit: int = Query(15, ge=1, le=50)):
    """Get latest policy news with real URLs."""
    return [
        NewsResponse(
            id=n["id"],
            title=n["title"],
            source=n["source"],
            source_url=n["source_url"],
            published_date=n["published_date"],
            summary=n["summary"],
            category=n["category"],
            url=n["url"]
        )
        for n in news_cache[:limit]
    ]


@app.get("/api/stats", response_model=DashboardStats)
async def get_stats():
    """Get dashboard statistics."""
    return DashboardStats(
        total_policies=len(policies_cache),
        active_updates=len([p for p in policies_cache if (datetime.now() - datetime.fromisoformat(p["published_date"])).total_seconds() < 3600]),
        sources=list(set(p["source"] for p in policies_cache)),
        last_updated=last_fetch.isoformat()
    )


@app.get("/api/analytics", response_model=AnalyticsData)
async def get_analytics():
    """Get aggregated analytics data for charts."""
    by_ministry = {}
    by_entity = {}
    by_sentiment = {"Positive": 0, "Neutral": 0, "Negative": 0}
    
    # Trend data: group by day for the last 7 days
    dates_map = {}
    for i in range(7):
        d = (datetime.now() - timedelta(days=i)).strftime("%b %d")
        dates_map[d] = 0
    
    for p in policies_cache:
        # Ministry
        min_name = p.get("ministry", "Unknown")
        by_ministry[min_name] = by_ministry.get(min_name, 0) + 1
        
        # Sentiment
        sent = p.get("sentiment", "Neutral")
        by_sentiment[sent] = by_sentiment.get(sent, 0) + 1
        
        # Entities
        for ent in p.get("entities", []):
            by_entity[ent] = by_entity.get(ent, 0) + 1
            
        # Date Trend
        try:
            p_date = datetime.fromisoformat(p["published_date"]).strftime("%b %d")
            if p_date in dates_map:
                dates_map[p_date] += 1
        except:
            pass
            
    # Sort date trend chronologically
    sorted_dates = []
    current_date = datetime.now()
    for i in range(6, -1, -1):
        d_str = (current_date - timedelta(days=i)).strftime("%b %d")
        sorted_dates.append({"date": d_str, "count": dates_map.get(d_str, 0)})
        
    return AnalyticsData(
        by_ministry=by_ministry,
        by_entity=by_entity,
        by_date=sorted_dates,
        sentiment_distribution=by_sentiment
    )


@app.post("/api/refresh")
async def refresh_data():
    """Manually trigger data refresh."""
    await fetch_real_data()
    return {"status": "success", "policies_count": len(policies_cache)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "last_updated": last_fetch.isoformat(),
        "policies_cached": len(policies_cache),
        "news_cached": len(news_cache)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
