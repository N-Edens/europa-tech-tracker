"""
Deduplication Module for Europa Tech Tracker
Handles duplicate article detection and removal based on URL, title similarity, and content
"""

import json
import hashlib
from datetime import datetime, timedelta
import difflib
from urllib.parse import urlparse, parse_qs
import re
from typing import List, Dict, Set


class ArticleDeduplicator:
    """Handle duplicate article detection and removal"""
    
    def __init__(self, cache_file_path="data/cache/seen_urls.json", similarity_threshold=0.8):
        self.cache_file = cache_file_path
        self.similarity_threshold = similarity_threshold
        self.seen_urls = self._load_url_cache()
        self.title_hashes = set()
        
    def remove_duplicates(self, articles, max_age_days=7):
        """
        Remove duplicate articles based on URL and title similarity
        
        Args:
            articles (list): List of article dictionaries
            max_age_days (int): Maximum age to keep URLs in cache
        
        Returns:
            list: Deduplicated articles
        """
        print(f"   🔍 Deduplicating {len(articles)} articles...")
        
        # Clean old entries from cache
        self._clean_old_entries(max_age_days)
        
        unique_articles = []
        processed_urls = set()
        processed_titles = set()
        
        for article in articles:
            # Check URL duplicates
            normalized_url = self._normalize_url(article.get('url', ''))
            
            if self._is_duplicate_url(normalized_url):
                continue
                
            # Check title similarity
            title = article.get('title', '')
            if self._is_duplicate_title(title, processed_titles):
                continue
            
            # Article is unique - add to results
            unique_articles.append(article)
            
            # Update tracking sets
            processed_urls.add(normalized_url)
            processed_titles.add(title.lower().strip())
            
            # Update cache
            self._add_to_cache(normalized_url)
        
        # Save updated cache
        self._save_url_cache()
        
        removed_count = len(articles) - len(unique_articles)
        print(f"   ✅ Removed {removed_count} duplicates, kept {len(unique_articles)} unique articles")
        
        return unique_articles
    
    def _normalize_url(self, url):
        """Normalize URL for consistent comparison"""
        if not url:
            return ""
        
        # Parse URL
        parsed = urlparse(url.lower())
        
        # Remove common tracking parameters
        tracking_params = {
            'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
            'fbclid', 'gclid', 'ref', 'source', '_source', 'campaign'
        }
        
        # Rebuild query string without tracking parameters
        query_params = parse_qs(parsed.query)
        clean_params = {k: v for k, v in query_params.items() if k not in tracking_params}
        
        # Handle common URL variations
        path = parsed.path.rstrip('/')
        if path == '':
            path = '/'
        
        # Rebuild clean URL
        clean_url = f"{parsed.scheme}://{parsed.netloc}{path}"
        
        if clean_params:
            param_string = '&'.join(f"{k}={v[0]}" for k, v in clean_params.items())
            clean_url += f"?{param_string}"
        
        return clean_url
    
    def _is_duplicate_url(self, url):
        """Check if URL has been seen before"""
        return url in self.seen_urls
    
    def _is_duplicate_title(self, title, processed_titles):
        """Check if title is too similar to already processed ones"""
        if not title:
            return False
            
        clean_title = self._clean_title(title)
        
        # Check exact matches first (fast)
        if clean_title in processed_titles:
            return True
        
        # Check similarity for near-duplicates
        for existing_title in processed_titles:
            similarity = difflib.SequenceMatcher(None, clean_title, existing_title).ratio()
            if similarity >= self.similarity_threshold:
                return True
        
        return False
    
    def _clean_title(self, title):
        """Clean and normalize title for comparison"""
        if not title:
            return ""
        
        # Convert to lowercase
        clean = title.lower().strip()
        
        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            "breaking:", "exclusive:", "news:", "update:", "analysis:",
            "report:", "study:", "survey:", "interview:"
        ]
        
        suffixes_to_remove = [
            "- techcrunch", "- tech.eu", "- sifted", "- the next web",
            "| techcrunch", "| tech.eu", "| sifted", "| the next web"
        ]
        
        for prefix in prefixes_to_remove:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()
        
        for suffix in suffixes_to_remove:
            if clean.endswith(suffix):
                clean = clean[:-len(suffix)].strip()
        
        # Normalize whitespace and remove special characters
        clean = re.sub(r'\s+', ' ', clean)
        clean = re.sub(r'[^\w\s]', '', clean)
        
        return clean
    
    def _add_to_cache(self, url):
        """Add URL to seen cache with timestamp"""
        if url:
            self.seen_urls[url] = datetime.now().isoformat()
    
    def _load_url_cache(self):
        """Load seen URLs from cache file"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_url_cache(self):
        """Save seen URLs to cache file"""
        try:
            # Ensure directory exists
            import os
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.seen_urls, f, indent=2)
        except Exception as e:
            print(f"   ⚠️  Error saving URL cache: {e}")
    
    def _clean_old_entries(self, max_age_days):
        """Remove old entries from cache"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        old_urls = []
        for url, timestamp_str in self.seen_urls.items():
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                if timestamp < cutoff_date:
                    old_urls.append(url)
            except (ValueError, AttributeError):
                # Invalid timestamp - mark for removal
                old_urls.append(url)
        
        for url in old_urls:
            del self.seen_urls[url]
        
        if old_urls:
            print(f"   🧹 Cleaned {len(old_urls)} old URLs from cache")
    
    def get_cache_stats(self):
        """Get statistics about the cache"""
        total_urls = len(self.seen_urls)
        
        # Count by age
        now = datetime.now()
        age_breakdown = {'today': 0, 'week': 0, 'month': 0, 'older': 0}
        
        for timestamp_str in self.seen_urls.values():
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', ''))
                age = (now - timestamp).days
                
                if age == 0:
                    age_breakdown['today'] += 1
                elif age <= 7:
                    age_breakdown['week'] += 1
                elif age <= 30:
                    age_breakdown['month'] += 1
                else:
                    age_breakdown['older'] += 1
            except (ValueError, AttributeError):
                age_breakdown['older'] += 1
        
        return {
            'total_urls': total_urls,
            'age_breakdown': age_breakdown,
            'cache_file': self.cache_file,
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear_cache(self):
        """Clear all cached URLs (use with caution)"""
        self.seen_urls = {}
        self._save_url_cache()
        print("   🗑️  URL cache cleared")
    
    def find_potential_duplicates(self, articles, threshold=0.7):
        """Find potential duplicate groups for manual review"""
        potential_groups = []
        
        for i, article1 in enumerate(articles):
            for j, article2 in enumerate(articles[i+1:], i+1):
                title1 = self._clean_title(article1.get('title', ''))
                title2 = self._clean_title(article2.get('title', ''))
                
                similarity = difflib.SequenceMatcher(None, title1, title2).ratio()
                
                if similarity >= threshold:
                    potential_groups.append({
                        'similarity': similarity,
                        'article1': {
                            'title': article1.get('title', ''),
                            'url': article1.get('url', ''),
                            'source': article1.get('source', '')
                        },
                        'article2': {
                            'title': article2.get('title', ''),
                            'url': article2.get('url', ''),
                            'source': article2.get('source', '')
                        }
                    })
        
        return sorted(potential_groups, key=lambda x: x['similarity'], reverse=True)