"""Base scraper class for policy data collection."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyDocument:
    """Represents a policy document from a government source."""
    id: str
    title: str
    type: str  # bill, act, notification, regulation
    source: str
    source_url: str
    ministry: str
    published_date: datetime
    summary: str
    impact: str
    entities: List[str] = field(default_factory=list)
    full_text: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.now)


@dataclass
class NewsArticle:
    """Represents a news article related to policies."""
    id: str
    title: str
    source: str
    source_url: str
    published_date: datetime
    summary: str
    category: str = "general"
    scraped_at: datetime = field(default_factory=datetime.now)


class BaseScraper(ABC):
    """Base class for all scrapers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = logging.getLogger(f"scraper.{source_name}")
    
    @abstractmethod
    async def fetch_policies(self, limit: int = 10) -> List[PolicyDocument]:
        """Fetch latest policies from the source."""
        pass
    
    @abstractmethod
    async def fetch_news(self, limit: int = 10) -> List[NewsArticle]:
        """Fetch latest news from the source."""
        pass
    
    async def fetch_all(self, policy_limit: int = 10, news_limit: int = 10) -> Dict[str, Any]:
        """Fetch both policies and news."""
        policies, news = await asyncio.gather(
            self.fetch_policies(policy_limit),
            self.fetch_news(news_limit)
        )
        return {
            "source": self.source_name,
            "policies": policies,
            "news": news,
            "scraped_at": datetime.now()
        }
    
    def _generate_id(self, text: str) -> str:
        """Generate a unique ID from text."""
        import hashlib
        return hashlib.md5(text.encode()).hexdigest()[:12]
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from various formats."""
        import dateparser
        try:
            return dateparser.parse(date_str)
        except:
            return None
