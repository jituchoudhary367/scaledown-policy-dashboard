"""
High-Density Policy Content Summarizer
Works with or without OpenAI - falls back to rule-based summarization when API unavailable
"""
import os
import json
import re
from typing import List, Dict, Any, Optional

# Try to import OpenAI, but provide fallback if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Only create client if API key is available
client = None
if OPENAI_API_KEY and OPENAI_AVAILABLE:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None


class PolicySummarizer:
    """
    High-density policy content summarizer using ScaleDown principles:
    - Semantic condensation
    - Redundancy elimination  
    - Context prioritization
    
    Falls back to rule-based summarization when LLM is unavailable.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.use_llm = client is not None
        self.compression_prompt = """You are a policy compression expert using ScaleDown principles.
Your task is to compress policy content while preserving essential information.

ScaleDown Principles:
1. REDUNDANCY ELIMINATION: Remove repeated phrases like "Notwithstanding anything contained..."
2. SEMANTIC CONDENSATION: Convert verbose statements to compact representations
3. CONTEXT PRIORITIZATION: Keep policy-meaningful sentences, remove procedural language

Input: Raw policy text
Output: Compressed structured representation with:
- policy_name: Name of the policy
- summary: Brief 2-3 sentence summary
- affected_entities: Who/what is affected (startups, citizens, businesses, etc.)
- key_rules: List of key requirements (compact)
- penalties: List of penalties (compact)
- relevant_date: Any important dates mentioned

Keep output as JSON only, no additional text."""

    def _strip_html(self, html_content: str) -> str:
        """
        Strip all HTML tags and extract clean text content.
        Handles common HTML patterns and converts to readable text.
        """
        if not html_content:
            return ""
        
        text = html_content
        
        # Remove script and style elements completely
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Replace common block elements with newlines
        for tag in ['<br>', '<br/>', '<br />', '</p>', '</div>', '</li>', '</tr>', '</th>', '</td>', '</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>', '</section>', '</article>', '</header>', '</footer>', '</nav>', '</main>']:
            text = text.replace(tag, '\n')
        
        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&rsquo;', "'")
        text = text.replace('&lsquo;', "'")
        text = text.replace('&rdquo;', '"')
        text = text.replace('&ldquo;', '"')
        text = text.replace('&mdash;', '-')
        text = text.replace('&ndash;', '-')
        text = text.replace('&hellip;', '...')
        
        # Remove navigation-related keywords and patterns
        nav_patterns = [
            r'\bDecrease Font Size\b.*?(?=\b[A-Z]|$)',
            r'\bNormal Font Size\b.*?(?=\b[A-Z]|$)',
            r'\bIncrease Font Size\b.*?(?=\b[A-Z]|$)',
            r'\bHigh Contrast\b.*?(?=\b[A-Z]|$)',
            r'\bNormal Theme\b.*?(?=\b[A-Z]|$)',
            r'\bGovernment of India\b.*?(?=\b[A-Z]|$)',
            r'={3,}',
            r'-{3,}',
        ]
        for pattern in nav_patterns:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def summarize(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        Create high-density summary of policy content
        
        Args:
            content: Raw policy content
            title: Optional title
            
        Returns:
            Dictionary with compressed policy information
        """
        if not content or len(content.strip()) < 50:
            return {
                "summary": "Content too short to summarize",
                "affected_entities": [],
                "key_rules": [],
                "penalties": [],
                "relevant_date": None,
                "policy_name": title
            }
        
        # Try LLM summarization first
        if self.use_llm:
            try:
                return self._llm_summarize(content, title)
            except Exception as e:
                # If LLM fails, fall back to rule-based
                if "quota" in str(e).lower() or "insufficient" in str(e).lower():
                    print(f"LLM quota exceeded, using rule-based summarization")
                    self.use_llm = False
        
        # Fall back to rule-based summarization
        return self._rule_based_summarize(content, title)
    
    def _llm_summarize(self, content: str, title: str) -> Dict[str, Any]:
        """Use LLM for summarization"""
        # Limit content to avoid token limits
        max_chars = 8000
        truncated_content = content[:max_chars] if len(content) > max_chars else content
        
        prompt = f"""{self.compression_prompt}

Policy Title: {title}

Content to compress:
{truncated_content}

Output (JSON only):"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a policy compression expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        result = response.choices[0].message.content
        
        # Parse JSON from response
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                summary_data = json.loads(result[json_start:json_end])
            else:
                summary_data = {"summary": result}
        except json.JSONDecodeError:
            summary_data = {"summary": result}
        
        return {
            "summary": summary_data.get("summary", "Summary not available"),
            "affected_entities": summary_data.get("affected_entities", []),
            "key_rules": summary_data.get("key_rules", []),
            "penalties": summary_data.get("penalties", []),
            "relevant_date": summary_data.get("relevant_date"),
            "policy_name": summary_data.get("policy_name", title)
        }
    
    def _rule_based_summarize(self, content: str, title: str) -> Dict[str, Any]:
        """
        Rule-based summarization without LLM
        Uses pattern matching to extract key information
        Generates 200-300 word summary with paragraphs and key points
        """
        # First, strip ALL HTML tags to get clean text
        cleaned_content = self._strip_html(content)
        
        # If we got very little meaningful content after cleaning, try content field
        if len(cleaned_content.strip()) < 100:
            cleaned_content = content
        
        # Additional cleaning - remove special characters and unwanted patterns
        cleaned_content = re.sub(r'#+\s*', '', cleaned_content)  # Remove hashtags
        cleaned_content = re.sub(r'\*+', '', cleaned_content)  # Remove asterisks
        cleaned_content = re.sub(r'\[Image[^\]]*\]', '', cleaned_content)  # Remove Image references
        cleaned_content = re.sub(r'Image \d+:', '', cleaned_content)  # Remove Image references
        cleaned_content = re.sub(r'\[.*?\]\(.*?\)', '', cleaned_content)  # Remove markdown links
        cleaned_content = re.sub(r'!\[[^\]]*\]\([^\)]*\)', '', cleaned_content)  # Remove images
        cleaned_content = re.sub(r'http[s]?://\S+', '', cleaned_content)  # Remove URLs
        cleaned_content = re.sub(r'\s+', ' ', cleaned_content).strip()
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', cleaned_content)
        
        # Filter out very short sentences and noise
        meaningful_sentences = [s for s in sentences if len(s) > 30]
        
        # Build summary with multiple paragraphs (200-300 words)
        summary_parts = []
        
        # First paragraph: Introduction - what is this policy about
        if meaningful_sentences:
            intro_sentences = []
            word_count = 0
            for sent in meaningful_sentences[:8]:
                intro_sentences.append(sent)
                word_count += len(sent.split())
                if word_count >= 80:
                    break
            if intro_sentences:
                summary_parts.append(' '.join(intro_sentences))
        
        # Second paragraph: Key provisions and requirements
        key_words = ['shall', 'must', 'required', 'mandatory', 'provide', 'ensure', 'implement', 'establish', 'create', 'require', 'according', 'under', 'pursuant']
        provision_sentences = []
        word_count = 0
        for sent in meaningful_sentences[5:20]:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in key_words):
                provision_sentences.append(sent)
                word_count += len(sent.split())
                if word_count >= 80:
                    break
        if provision_sentences:
            summary_parts.append(' '.join(provision_sentences))
        
        # Third paragraph: Benefits, impact and who it affects
        impact_words = ['benefit', 'advantage', 'increase', 'improve', 'support', 'promote', 'encourage', 'facilitate', 'enable', 'aim', 'objective', 'purpose']
        impact_sentences = []
        word_count = 0
        for sent in meaningful_sentences[10:30]:
            sent_lower = sent.lower()
            if any(kw in sent_lower for kw in impact_words):
                impact_sentences.append(sent)
                word_count += len(sent.split())
                if word_count >= 60:
                    break
        if impact_sentences:
            summary_parts.append(' '.join(impact_sentences))
        
        # Combine all parts into final summary
        summary = '\n\n'.join(summary_parts)
        
        # Ensure it's at least 200 words
        final_word_count = len(summary.split())
        if final_word_count < 200 and meaningful_sentences:
            additional_sentences = []
            word_count = 0
            for sent in meaningful_sentences[20:40]:
                additional_sentences.append(sent)
                word_count += len(sent.split())
                if word_count >= 100:
                    break
            if additional_sentences:
                summary = summary + '\n\n' + ' '.join(additional_sentences)
        
        # Final cleanup
        summary = re.sub(r'\s+', ' ', summary).strip()
        summary = re.sub(r'[#*]', '', summary)
        
        # Extract dates
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        relevant_date = dates[0] if dates else None
        
        # Extract key entities
        entities = self._extract_entities(content, title)
        
        # Extract key rules and penalties
        key_rules = self._extract_rules(content)
        penalties = self._extract_penalties(content)
        
        return {
            "summary": summary[:2000] if summary else "Summary not available",
            "affected_entities": entities,
            "key_rules": key_rules,
            "penalties": penalties,
            "relevant_date": relevant_date,
            "policy_name": title
        }
    
    def _extract_entities(self, content: str, title: str) -> List[str]:
        """Extract affected entities from content"""
        entities = set()
        
        # Common entity patterns
        entity_patterns = {
            "Startups": r'\bstartup[s]?\b',
            "Businesses": r'\bbusiness(es)?\b',
            "Small Businesses": r'\bsmall\s+business\b',
            "Taxpayers": r'\btaxpayer[s]?\b',
            "Citizens": r'\bcitizen[s]?\b',
            "Students": r'\bstudent[s]?\b',
            "Farmers": r'\bfarmer[s]?\b',
            "Companies": r'\bcompan(y|ies)\b',
            "Industries": r'\bindustr(y|ies)\b',
            "Government": r'\bgovernment\b',
        }
        
        content_lower = content.lower()
        for entity, pattern in entity_patterns.items():
            if re.search(pattern, content_lower):
                entities.add(entity)
        
        return list(entities)[:5]  # Limit to 5 entities
    
    def _extract_rules(self, content: str) -> List[str]:
        """Extract key rules/requirements from content"""
        rules = []
        
        # Patterns indicating rules
        rule_patterns = [
            r'shall\s+be\s+required\s+to\s+([^.]+)',
            r'must\s+([^.]+(?:comply|submit|obtain|provide|ensure)[^.]+)',
            r'is\s+required\s+to\s+([^.]+)',
            r'compulsory\s+to\s+([^.]+)',
            r'no\s+[^.]+(?:shall|may|can)\s+([^.]+)',
        ]
        
        for pattern in rule_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            rules.extend([m.strip()[:100] for m in matches[:3]])
        
        return list(set(rules))[:5]  # Dedupe and limit
    
    def _extract_penalties(self, content: str) -> List[str]:
        """Extract penalties from content"""
        penalties = []
        
        # Patterns indicating penalties
        penalty_patterns = [
            r'penalty\s+(?:of|up to|not exceeding)\s+([^.]+)',
            r'fine\s+(?:of|up to)\s+([^.]+)',
            r'imprisonment\s+(?:for|up to)\s+([^.]+)',
            r'liable\s+(?:to|for)\s+([^.]+(?:penalty|fine|damages)[^.]+)',
            r'penalty\s+[^.]+(?:₹|INR|rupee|paise)\s*\d+',
        ]
        
        for pattern in penalty_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            penalties.extend([m.strip()[:100] for m in matches[:3]])
        
        return list(set(penalties))[:5]  # Dedupe and limit
    
    def batch_summarize(self, items: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Summarize multiple policy items
        
        Args:
            items: List of dicts with 'content' and optionally 'title'
            
        Returns:
            List of summary dictionaries
        """
        results = []
        for item in items:
            summary = self.summarize(
                content=item.get("content", ""),
                title=item.get("title", "")
            )
            results.append(summary)
        return results


# Singleton instance
_summarizer: Optional[PolicySummarizer] = None


def get_summarizer() -> PolicySummarizer:
    """Get or create the policy summarizer instance"""
    global _summarizer
    if _summarizer is None:
        _summarizer = PolicySummarizer()
    return _summarizer
