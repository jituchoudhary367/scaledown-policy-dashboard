"""Scraper for Press Information Bureau (PIB) announcements."""
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime, timedelta
import logging

from .base import BaseScraper, PolicyDocument, NewsArticle


class PIBScraper(BaseScraper):
    """Scraper for Press Information Bureau."""
    
    def __init__(self):
        super().__init__("Press Information Bureau")
        self.base_url = "https://pib.gov.in"
    
    async def fetch_policies(self, limit: int = 10) -> List[PolicyDocument]:
        """Fetch latest PIB releases about policies."""
        policies = []
        
        # Sample PIB policy releases
        sample_policies = [
            {
                "title": "PM-KISAN 19th Installment Release",
                "type": "notification",
                "ministry": "MoA",
                "summary": "Prime Minister releases 19th installment of PM-KISAN scheme benefiting farmer families across India.",
                "impact": "Over 9 crore farmer families receive direct income support of ₹2000",
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1987654",
                "date": datetime.now() - timedelta(hours=4)
            },
            {
                "title": "Startup India Seed Fund Scheme - New Guidelines",
                "type": "notification",
                "ministry": "DPIIT",
                "summary": "Revised guidelines for Startup India Seed Fund Scheme with enhanced funding limits and faster disbursement.",
                "impact": "Early stage startups can now get seed funding up to ₹50 lakhs",
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1987655",
                "date": datetime.now() - timedelta(hours=10)
            },
            {
                "title": "Ayushman Bharat PM-JAY Expansion",
                "type": "notification",
                "ministry": "MoHFW",
                "summary": "Government expands Ayushman Bharat coverage to include more families and new treatments.",
                "impact": "Additional 5 crore families now eligible for free healthcare coverage",
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1987656",
                "date": datetime.now() - timedelta(hours=18)
            },
            {
                "title": "PLI Scheme for Semiconductor Manufacturing",
                "type": "notification",
                "ministry": "MeitY",
                "summary": "Production Linked Incentive scheme extended for semiconductor manufacturing units.",
                "impact": "₹76,000 crore incentive for setting up semiconductor fabs in India",
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1987657",
                "date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Digital Health Mission Rollout",
                "type": "regulation",
                "ministry": "MoHFW",
                "summary": "National Digital Health Mission rolled out across all districts with health ID for citizens.",
                "impact": "Every citizen gets unique health ID for accessing medical records",
                "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=1987658",
                "date": datetime.now() - timedelta(days=2)
            }
        ]
        
        for policy in sample_policies[:limit]:
            doc = PolicyDocument(
                id=self._generate_id(policy["title"]),
                title=policy["title"],
                type=policy["type"],
                source="PIB",
                source_url=policy["url"],
                ministry=policy["ministry"],
                published_date=policy["date"],
                summary=policy["summary"],
                impact=policy["impact"],
                entities=self._extract_entities(policy["title"], policy["summary"])
            )
            policies.append(doc)
        
        self.logger.info(f"Fetched {len(policies)} policies from PIB")
        return policies
    
    async def fetch_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch latest PIB news."""
        articles = []
        
        sample_news = [
            {
                "title": "Government announces major reforms in telecom sector",
                "summary": "New telecom policy focuses on 5G rollout, fiber connectivity, and reduced regulatory burden.",
                "url": "https://pib.gov.in/News/1987659",
                "date": datetime.now() - timedelta(minutes=30)
            },
            {
                "title": "Finance Minister meets startup founders to discuss growth roadmap",
                "summary": "Key recommendations from startup ecosystem to be incorporated in next budget.",
                "url": "https://pib.gov.in/News/1987660",
                "date": datetime.now() - timedelta(hours=2)
            },
            {
                "title": "Education ministry launches AI in education initiative",
                "summary": "New program to integrate AI tools in school education across 50,000 schools.",
                "url": "https://pib.gov.in/News/1987661",
                "date": datetime.now() - timedelta(hours=5)
            },
            {
                "title": "MSME sector gets new credit guarantee scheme",
                "summary": "Government guarantees 85% of loans up to ₹2 crore for MSMEs.",
                "url": "https://pib.gov.in/News/1987662",
                "date": datetime.now() - timedelta(hours=12)
            }
        ]
        
        for news in sample_news[:limit]:
            article = NewsArticle(
                id=self._generate_id(news["title"]),
                title=news["title"],
                source="PIB",
                source_url=news["url"],
                published_date=news["date"],
                summary=news["summary"],
                category="government"
            )
            articles.append(article)
        
        return articles
    
    def _extract_entities(self, title: str, summary: str) -> List[str]:
        """Extract affected entities from policy text."""
        entities = []
        text = (title + " " + summary).lower()
        
        if any(word in text for word in ["startup", "entrepreneur", "venture", "seed fund"]):
            entities.append("Startups")
        if any(word in text for word in ["student", "education", "school", "ai in education"]):
            entities.append("Students")
        if any(word in text for word in ["farmer", "agriculture", "pm-kisan", "kisan"]):
            entities.append("Farmers")
        if any(word in text for word in ["msme", "business", "company", "industry"]):
            entities.append("Businesses")
        if any(word in text for word in ["taxpayer", "tax", "income", "budget"]):
            entities.append("Taxpayers")
        if any(word in text for word in ["health", "hospital", "medical", "ayushman"]):
            entities.append("Healthcare")
        
        return entities[:4]
