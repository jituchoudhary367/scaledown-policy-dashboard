"""Policy scrapers package."""
from .base import BaseScraper, PolicyDocument, NewsArticle
from .parliament import ParliamentScraper
from .pib import PIBScraper
from .government import MeitYScraper, GazetteScraper

__all__ = [
    'BaseScraper',
    'PolicyDocument', 
    'NewsArticle',
    'ParliamentScraper',
    'PIBScraper',
    'MeitYScraper',
    'GazetteScraper'
]
