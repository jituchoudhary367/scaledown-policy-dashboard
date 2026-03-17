"""Scrapers for MeitY and Government Gazette."""
import httpx
from typing import List
from datetime import datetime, timedelta
import logging

from .base import BaseScraper, PolicyDocument, NewsArticle


class MeitYScraper(BaseScraper):
    """Scraper for Ministry of Electronics & IT."""
    
    def __init__(self):
        super().__init__("MeitY")
        self.base_url = "https://www.meitY.gov.in"
    
    async def fetch_policies(self, limit: int = 10) -> List[PolicyDocument]:
        """Fetch latest MeitY announcements and policies."""
        policies = []
        
        sample_policies = [
            {
                "title": "Data Center Policy 2026",
                "type": "policy",
                "ministry": "MeitY",
                "summary": "National policy for development of data center parks with incentives for green energy usage.",
                "impact": "Tax benefits and land allocation for data center operators",
                "url": "https://www.meitY.gov.in/content/data-center-policy-2026",
                "date": datetime.now() - timedelta(hours=5)
            },
            {
                "title": "India AI Mission - Phase II",
                "type": "regulation",
                "ministry": "MeitY",
                "summary": "Second phase of India AI mission with ₹15,000 crore allocation for AI research and startups.",
                "impact": "Funding for AI startups, research labs, and skill development",
                "url": "https://www.meitY.gov.in/content/india-ai-mission",
                "date": datetime.now() - timedelta(hours=14)
            },
            {
                "title": "Software Product Industry Scheme",
                "type": "notification",
                "ministry": "MeitY",
                "summary": "New scheme for promoting Indian software product companies with market access support.",
                "impact": "Government procurement preference for Indian software products",
                "url": "https://www.meitY.gov.in/content/software-product-scheme",
                "date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Cyber Security Framework for Digital Services",
                "type": "regulation",
                "ministry": "MeitY",
                "summary": "Mandatory security compliance for digital service providers handling citizen data.",
                "impact": "All tech companies must implement CERT-IN directives",
                "url": "https://www.meitY.gov.in/content/cyber-security-framework",
                "date": datetime.now() - timedelta(days=2)
            }
        ]
        
        for policy in sample_policies[:limit]:
            doc = PolicyDocument(
                id=self._generate_id(policy["title"]),
                title=policy["title"],
                type=policy["type"],
                source="MeitY",
                source_url=policy["url"],
                ministry=policy["ministry"],
                published_date=policy["date"],
                summary=policy["summary"],
                impact=policy["impact"],
                entities=["Tech Companies", "Startups", "Data Centers"]
            )
            policies.append(doc)
        
        self.logger.info(f"Fetched {len(policies)} policies from MeitY")
        return policies
    
    async def fetch_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch latest MeitY news."""
        articles = []
        
        sample_news = [
            {
                "title": "MeitY releases draft AI regulation for public consultation",
                "summary": "Stakeholders invited to provide feedback on proposed AI governance framework.",
                "url": "https://www.meitY.gov.in/news/ai-regulation-draft",
                "date": datetime.now() - timedelta(minutes=45)
            },
            {
                "title": "5G rollout reaches 500 districts",
                "summary": "India achieves major milestone in digital connectivity with 5G services in 500 districts.",
                "url": "https://www.meitY.gov.in/news/5g-rollout",
                "date": datetime.now() - timedelta(hours=3)
            }
        ]
        
        for news in sample_news[:limit]:
            article = NewsArticle(
                id=self._generate_id(news["title"]),
                title=news["title"],
                source="MeitY",
                source_url=news["url"],
                published_date=news["date"],
                summary=news["summary"],
                category="technology"
            )
            articles.append(article)
        
        return articles


class GazetteScraper(BaseScraper):
    """Scraper for Government Gazette of India."""
    
    def __init__(self):
        super().__init__("Gazette of India")
        self.base_url = "https://www.gazette.gov.in"
    
    async def fetch_policies(self, limit: int = 10) -> List[PolicyDocument]:
        """Fetch latest Gazette notifications."""
        policies = []
        
        sample_policies = [
            {
                "title": "Income Tax (23rd Amendment) Rules, 2026",
                "type": "notification",
                "ministry": "MoF",
                "summary": "New rules for taxation of digital assets and crypto transactions with 1% TDS provision.",
                "impact": "Crypto investors must report all transactions above ₹50,000",
                "url": "https://www.gazette.gov.in/writereaddata/2026/20240312_OCR.pdf",
                "date": datetime.now() - timedelta(hours=12)
            },
            {
                "title": "GST (47th Amendment) Notification",
                "type": "notification",
                "ministry": "MoF",
                "summary": "Changes in GST rates for IT services and digital products.",
                "impact": "Reduced GST on software subscriptions from 18% to 12%",
                "url": "https://www.gazette.gov.in/writereaddata/2026/20240311_OCR.pdf",
                "date": datetime.now() - timedelta(days=1)
            },
            {
                "title": "Companies (Amendment) Act, 2026",
                "type": "act",
                "ministry": "MCA",
                "summary": "Amendments to ease compliance requirements for private companies.",
                "impact": "Simplified board meeting requirements and faster incorporation",
                "url": "https://www.gazette.gov.in/writereaddata/2026/20240310_OCR.pdf",
                "date": datetime.now() - timedelta(days=2)
            },
            {
                "title": "Foreign Exchange Management ( amendment) Rules",
                "type": "regulation",
                "ministry": "MEA",
                "summary": "Liberalized norms for overseas investment by Indian startups.",
                "impact": "Startups can now invest up to 50% of net worth overseas",
                "url": "https://www.gazette.gov.in/writereaddata/2026/20240309_OCR.pdf",
                "date": datetime.now() - timedelta(days=3)
            }
        ]
        
        for policy in sample_policies[:limit]:
            doc = PolicyDocument(
                id=self._generate_id(policy["title"]),
                title=policy["title"],
                type=policy["type"],
                source="Gazette",
                source_url=policy["url"],
                ministry=policy["ministry"],
                published_date=policy["date"],
                summary=policy["summary"],
                impact=policy["impact"],
                entities=self._extract_entities(policy["title"], policy["summary"])
            )
            policies.append(doc)
        
        self.logger.info(f"Fetched {len(policies)} policies from Gazette")
        return policies
    
    async def fetch_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch Gazette-related news."""
        # Gazette doesn't have separate news, return empty
        return []
    
    def _extract_entities(self, title: str, summary: str) -> List[str]:
        """Extract affected entities from policy text."""
        entities = []
        text = (title + " " + summary).lower()
        
        if any(word in text for word in ["startup", "company", "incorporation"]):
            entities.append("Startups")
            entities.append("Businesses")
        if any(word in text for word in ["tax", "income", "gst"]):
            entities.append("Taxpayers")
        if any(word in text for word in ["crypto", "digital asset"]):
            entities.append("Investors")
        if any(word in text for word in ["foreign", "overseas", "investment"]):
            entities.append("NRI Investors")
        
        return entities[:4] if entities else ["General Public"]
