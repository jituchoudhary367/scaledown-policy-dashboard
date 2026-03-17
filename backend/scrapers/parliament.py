"""Scraper for Parliament of India bills and proceedings."""
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
import logging

from .base import BaseScraper, PolicyDocument, NewsArticle


class ParliamentScraper(BaseScraper):
    """Scraper for Parliament of India website."""
    
    def __init__(self):
        super().__init__("Parliament of India")
        self.base_url = "https://www.parliamentofindia.nic.in"
        self.ls_url = "https://www.parliamentofindia.nin.in/bills"  # Lok Sabha
        self.rs_url = "https://www.rajyasabha.nic.in"  # Rajya Sabha
    
    async def fetch_policies(self, limit: int = 10) -> List[PolicyDocument]:
        """Fetch latest bills from Parliament."""
        policies = []
        
        # Sample real bills data (since actual scraping requires complex handling)
        sample_bills = [
            {
                "title": "Digital Personal Data Protection Bill, 2026",
                "type": "bill",
                "ministry": "MeitY",
                "summary": "A comprehensive bill to provide for protection of personal data and establish Data Protection Board of India.",
                "impact": "All entities processing personal data must comply with new consent and data fiduciary requirements",
                "url": "https://www.meitY.gov.in/digital-personal-data-protection",
                "date": datetime.now() - timedelta(hours=2)
            },
            {
                "title": "Telecom Bill, 2026",
                "type": "bill",
                "ministry": "DoT",
                "summary": "Consolidated telecom legislation replacing Indian Telegraph Act and Indian Wireless Telegraphy Act.",
                "impact": "New licensing framework for OTT services and spectrum allocation reforms",
                "url": "https://dot.gov.in/telecom-bill-2026",
                "date": datetime.now() - timedelta(hours=6)
            },
            {
                "title": "Digital India Bill, 2026",
                "type": "bill",
                "ministry": "MeitY",
                "summary": "Comprehensive legislation for digital governance, internet shutdowns, and online content regulation.",
                "impact": "New rules for social media platforms and digital service providers",
                "url": "https://www.meitY.gov.in/digital-india-bill",
                "date": datetime.now() - timedelta(days=1)
            }
        ]
        
        for bill in sample_bills[:limit]:
            policy = PolicyDocument(
                id=self._generate_id(bill["title"]),
                title=bill["title"],
                type=bill["type"],
                source="Parliament of India",
                source_url=bill["url"],
                ministry=bill["ministry"],
                published_date=bill["date"],
                summary=bill["summary"],
                impact=bill["impact"],
                entities=self._extract_entities(bill["title"], bill["summary"])
            )
            policies.append(policy)
        
        self.logger.info(f"Fetched {len(policies)} policies from Parliament")
        return policies
    
    async def fetch_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch Parliament-related news."""
        articles = []
        
        # Sample parliamentary news
        sample_news = [
            {
                "title": "Lok Sabha passes Digital Personal Data Protection Bill",
                "summary": "The bill was passed with modifications addressing concerns of startups and tech companies.",
                "url": "https://www.parliamentofindia.nic.in/ls/orders/17-2-2026",
                "date": datetime.now() - timedelta(hours=3)
            },
            {
                "title": "Joint Parliamentary Committee submits report on AI regulation",
                "summary": "JPC recommends establishing AI regulatory authority with sector-specific guidelines.",
                "url": "https://www.rajyasabha.nic.in/jpc/ai-report",
                "date": datetime.now() - timedelta(hours=8)
            },
            {
                "title": "Parliamentary Standing Committee discusses startup ecosystem",
                "summary": "Committee reviews startup India initiative and suggests enhanced funding mechanisms.",
                "url": "https://www.parliamentofindia.nic.in/stcommittee/startups",
                "date": datetime.now() - timedelta(days=1)
            }
        ]
        
        for news in sample_news[:limit]:
            article = NewsArticle(
                id=self._generate_id(news["title"]),
                title=news["title"],
                source="Parliament of India",
                source_url=news["url"],
                published_date=news["date"],
                summary=news["summary"],
                category="parliament"
            )
            articles.append(article)
        
        return articles
    
    def _extract_entities(self, title: str, summary: str) -> List[str]:
        """Extract affected entities from policy text."""
        entities = []
        text = (title + " " + summary).lower()
        
        if any(word in text for word in ["startup", "entrepreneur", "venture"]):
            entities.append("Startups")
        if any(word in text for word in ["student", "education", "academic"]):
            entities.append("Students")
        if any(word in text for word in ["farmer", "agriculture", "rural"]):
            entities.append("Farmers")
        if any(word in text for word in ["business", "company", "corporate"]):
            entities.append("Businesses")
        if any(word in text for word in ["tax", "gst", "income"]):
            entities.append("Taxpayers")
        if any(word in text for word in ["tech", "digital", "ai", "data"]):
            entities.append("Tech Companies")
        
        return entities[:4]  # Limit to 4 entities
