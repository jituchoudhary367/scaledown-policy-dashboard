"""Tavily search integration for real-time policy data."""
import os
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TavilySearch:
    """Real-time search using Tavily API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com/search"
    
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for policy-related content."""
        if not self.api_key:
            logger.warning("Tavily API key not configured")
            return []
        
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,
            "include_raw_content": True,
            "include_images": False
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                        "raw_content": item.get("raw_content", ""),
                        "score": item.get("score", 0),
                        "published_date": item.get("published_date")
                    })
                
                return results
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []
    
    async def search_policy_news(self, topics: List[str] = None) -> List[Dict[str, Any]]:
        """Search for latest policy news from multiple topics."""
        if topics is None:
            topics = [
                "India government policy 2026",
                "MeitY announcements",
                "Parliament bills India",
                "Startup India policy",
                "Digital India regulations"
            ]
        
        all_results = []
        
        for topic in topics:
            results = await self.search(topic, max_results=5)
            all_results.extend(results)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Sort by score
        all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return all_results[:20]  # Return top 20


# Policy search queries for government sources
POLICY_QUERIES = {
    "parliament": [
        "Parliament of India bills 2026",
        "Lok Sabha bills latest",
        "Rajya Sabha proceedings"
    ],
    "meity": [
        "MeitY notifications 2026",
        "Digital India policy",
        "AI regulation India"
    ],
    "pib": [
        "Press Information Bureau India latest",
        "Government press releases",
        "PIB announcements"
    ],
    "gazette": [
        "Gazette of India notifications",
        "Government orders India"
    ]
}


async def get_all_policy_data() -> Dict[str, List[Dict[str, Any]]]:
    """Get policy data from all sources via Tavily."""
    tavily = TavilySearch()
    
    results = {}
    
    for source, queries in POLICY_QUERIES.items():
        source_results = []
        for query in queries:
            search_results = await tavily.search(query, max_results=5)
            source_results.extend(search_results)
            await asyncio.sleep(0.5)
        
        results[source] = source_results
    
    return results
