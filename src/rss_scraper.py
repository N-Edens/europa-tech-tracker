"""
RSS Scraper Module for Europa Tech Tracker
Handles fetching and parsing RSS/Atom feeds from various European tech sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import re
import time


class RSScraper:
    """RSS/Atom feed scraper with error handling and rate limiting"""
    
    def __init__(self, request_timeout=30, rate_limit_delay=1.0):
        self.timeout = request_timeout
        self.rate_limit_delay = rate_limit_delay
        self.user_agent = "Europa-Tech-Tracker/1.0 (+https://github.com/N-Edens/europa-tech-tracker)"
        
        # Configure requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'
        })
    
    def fetch_articles(self, feed_url, source_name, max_age_days=7):
        """
        Fetch and parse articles from an RSS/Atom feed
        
        Args:
            feed_url (str): URL to the RSS/Atom feed
            source_name (str): Name identifier for the source
            max_age_days (int): Maximum age for articles in days
        
        Returns:
            list: List of article dictionaries
        """
        print(f"   🔗 Fetching feed: {feed_url}")
        
        try:
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            # Fetch feed with timeout
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo and feed.bozo_exception:
                print(f"   ⚠️  Feed parsing warning: {feed.bozo_exception}")
            
            # Validate feed
            if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                print(f"   ❌ No entries found in feed")
                return []
            
            # Process entries
            articles = []
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            for entry in feed.entries:
                article = self._parse_entry(entry, source_name, cutoff_date)
                if article:
                    articles.append(article)
            
            print(f"   ✅ Parsed {len(articles)} recent articles")
            return articles
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Network error fetching {feed_url}: {e}")
            return []
        except Exception as e:
            print(f"   ❌ Error processing feed {feed_url}: {e}")
            return []
    
    def _parse_entry(self, entry, source_name, cutoff_date):
        """
        Parse individual RSS/Atom entry into standardized article format
        
        Args:
            entry: feedparser entry object
            source_name (str): Source identifier
            cutoff_date (datetime): Cutoff date for articles
        
        Returns:
            dict: Parsed article or None if invalid/too old
        """
        try:
            # Get publication date
            pub_date = self._parse_date(entry)
            if pub_date and pub_date < cutoff_date:
                return None  # Article too old
            
            # Extract content
            title = self._clean_text(getattr(entry, 'title', 'No title'))
            description = self._extract_description(entry)
            content = self._extract_content(entry)
            
            # Build article object
            article = {
                'title': title,
                'description': description,
                'content': content,
                'url': getattr(entry, 'link', ''),
                'published': pub_date.isoformat() if pub_date else '',
                'source': source_name,
                'author': self._extract_author(entry),
                'tags': self._extract_tags(entry),
                'language': getattr(entry, 'language', 'en'),
                'word_count': len(content.split()) if content else 0
            }
            
            # Validation
            if not article['title'] or not article['url']:
                return None
            
            return article
            
        except Exception as e:
            print(f"   ⚠️  Error parsing entry: {e}")
            return None
    
    def _parse_date(self, entry):
        """Extract and parse publication date from entry"""
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                try:
                    time_tuple = getattr(entry, field)
                    return datetime(*time_tuple[:6])
                except (TypeError, ValueError):
                    continue
        
        # Fallback to string parsing
        date_strings = [
            getattr(entry, 'published', ''),
            getattr(entry, 'updated', ''),
            getattr(entry, 'created', '')
        ]
        
        for date_str in date_strings:
            if date_str:
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    continue
        
        return None
    
    def _extract_description(self, entry):
        """Extract article description/summary"""
        desc_fields = ['summary', 'description', 'subtitle']
        
        for field in desc_fields:
            if hasattr(entry, field):
                desc = getattr(entry, field)
                return self._clean_text(desc)
        
        return ''
    
    def _extract_content(self, entry):
        """Extract full article content"""
        # Try content field first
        if hasattr(entry, 'content') and entry.content:
            content_list = entry.content
            if isinstance(content_list, list) and content_list:
                return self._clean_text(content_list[0].get('value', ''))
        
        # Fallback to summary/description
        content = (
            getattr(entry, 'summary', '') or 
            getattr(entry, 'description', '') or
            getattr(entry, 'title', '')
        )
        
        return self._clean_text(content)
    
    def _extract_author(self, entry):
        """Extract author information"""
        if hasattr(entry, 'author'):
            return self._clean_text(entry.author)
        elif hasattr(entry, 'authors') and entry.authors:
            return self._clean_text(entry.authors[0].get('name', ''))
        return ''
    
    def _extract_tags(self, entry):
        """Extract tags/categories"""
        tags = []
        
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                if isinstance(tag, dict):
                    tags.append(tag.get('term', ''))
                else:
                    tags.append(str(tag))
        
        return [self._clean_text(tag) for tag in tags if tag]
    
    def _clean_text(self, text):
        """Clean and normalize text content"""
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', str(text))
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra newlines and spaces
        text = text.strip()
        
        return text
    
    def get_feed_info(self, feed_url):
        """Get metadata about an RSS feed (useful for debugging)"""
        try:
            response = self.session.get(feed_url, timeout=self.timeout)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            info = {
                'title': getattr(feed.feed, 'title', 'Unknown'),
                'description': getattr(feed.feed, 'description', ''),
                'link': getattr(feed.feed, 'link', ''),
                'language': getattr(feed.feed, 'language', ''),
                'total_entries': len(feed.entries),
                'last_updated': getattr(feed.feed, 'updated', ''),
                'generator': getattr(feed.feed, 'generator', ''),
                'feed_type': 'RSS' if feed.version.startswith('rss') else 'Atom' if feed.version.startswith('atom') else 'Unknown'
            }
            
            return info
            
        except Exception as e:
            return {'error': str(e)}