"""
Cache Management Module for Europa Tech Tracker
Handles article caching, metadata storage, and performance optimization
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class CacheManager:
    """Manage article caching and metadata storage"""
    
    def __init__(self, cache_dir="data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache file paths
        self.article_cache_file = self.cache_dir / "article_cache.json"
        self.metadata_cache_file = self.cache_dir / "metadata.json"
        self.stats_file = self.cache_dir / "daily_stats.json"
        
        # Load existing caches
        self.article_cache = self._load_json_file(self.article_cache_file)
        self.metadata = self._load_json_file(self.metadata_cache_file, {
            'last_update': None,
            'total_articles': 0,
            'sources_stats': {},
            'cache_created': datetime.now().isoformat()
        })
        
    def cache_articles(self, articles, source_name=None):
        """
        Cache articles with metadata and deduplication
        
        Args:
            articles (list): Articles to cache
            source_name (str): Source identifier
        
        Returns:
            dict: Caching statistics
        """
        cached_count = 0
        updated_count = 0
        
        for article in articles:
            article_hash = self._generate_article_hash(article)
            
            # Check if article exists in cache
            if article_hash in self.article_cache:
                # Update existing article if newer or more complete
                if self._should_update_cached_article(article, self.article_cache[article_hash]):
                    self.article_cache[article_hash] = self._prepare_article_for_cache(article)
                    updated_count += 1
            else:
                # Add new article to cache
                self.article_cache[article_hash] = self._prepare_article_for_cache(article)
                cached_count += 1
        
        # Update metadata
        self._update_source_stats(source_name, len(articles))
        self._save_caches()
        
        return {
            'new_cached': cached_count,
            'updated': updated_count,
            'total_processed': len(articles)
        }
    
    def get_recent_articles(self, hours=24, source=None, category=None):
        """
        Retrieve recently cached articles
        
        Args:
            hours (int): How many hours back to look
            source (str): Filter by source (optional)
            category (str): Filter by category (optional)
        
        Returns:
            list: Recent articles
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_articles = []
        
        for article_hash, article_data in self.article_cache.items():
            # Check if article is within time range
            try:
                cached_time = datetime.fromisoformat(article_data.get('cached_at', ''))
                if cached_time < cutoff:
                    continue
            except (ValueError, TypeError):
                continue
            
            # Apply filters
            if source and article_data.get('source') != source:
                continue
            if category and article_data.get('primary_category') != category:
                continue
            
            recent_articles.append(article_data)
        
        # Sort by cached time (newest first)
        recent_articles.sort(
            key=lambda x: x.get('cached_at', ''), 
            reverse=True
        )
        
        return recent_articles
    
    def get_cache_stats(self):
        """Get comprehensive cache statistics"""
        total_articles = len(self.article_cache)
        
        # Count by source
        source_breakdown = {}
        category_breakdown = {}
        date_breakdown = {}
        
        for article in self.article_cache.values():
            # Count by source
            source = article.get('source', 'unknown')
            source_breakdown[source] = source_breakdown.get(source, 0) + 1
            
            # Count by category
            category = article.get('primary_category', 'uncategorized')
            category_breakdown[category] = category_breakdown.get(category, 0) + 1
            
            # Count by date
            try:
                cached_date = datetime.fromisoformat(article.get('cached_at', '')).date()
                date_str = cached_date.isoformat()
                date_breakdown[date_str] = date_breakdown.get(date_str, 0) + 1
            except (ValueError, TypeError):
                pass
        
        # Calculate cache age
        cache_age_days = None
        if self.metadata.get('cache_created'):
            try:
                created = datetime.fromisoformat(self.metadata['cache_created'])
                cache_age_days = (datetime.now() - created).days
            except (ValueError, TypeError):
                pass
        
        return {
            'total_articles': total_articles,
            'cache_age_days': cache_age_days,
            'source_breakdown': source_breakdown,
            'category_breakdown': category_breakdown,
            'recent_dates': dict(sorted(date_breakdown.items(), reverse=True)[:7]),
            'cache_size_mb': self._get_cache_size_mb(),
            'last_update': self.metadata.get('last_update'),
            'metadata': self.metadata
        }
    
    def cleanup_old_articles(self, max_age_days=30):
        """
        Remove articles older than specified age
        
        Args:
            max_age_days (int): Maximum age in days
        
        Returns:
            int: Number of articles removed
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        articles_to_remove = []
        
        for article_hash, article_data in self.article_cache.items():
            try:
                cached_time = datetime.fromisoformat(article_data.get('cached_at', ''))
                if cached_time < cutoff_date:
                    articles_to_remove.append(article_hash)
            except (ValueError, TypeError):
                # Invalid timestamp - mark for removal
                articles_to_remove.append(article_hash)
        
        for article_hash in articles_to_remove:
            del self.article_cache[article_hash]
        
        if articles_to_remove:
            self._save_caches()
            print(f"   🧹 Cleaned up {len(articles_to_remove)} old articles from cache")
        
        return len(articles_to_remove)
    
    def search_cached_articles(self, query, limit=10):
        """
        Search cached articles by title and content
        
        Args:
            query (str): Search query
            limit (int): Maximum results
        
        Returns:
            list: Matching articles
        """
        query_lower = query.lower()
        results = []
        
        for article_data in self.article_cache.values():
            score = 0
            
            # Check title match
            title = article_data.get('title', '').lower()
            if query_lower in title:
                score += 3
            
            # Check content match
            content = article_data.get('content', '').lower()
            if query_lower in content:
                score += 1
            
            # Check keywords match
            keywords = article_data.get('matched_keywords', {})
            for category_keywords in keywords.values():
                for kw_info in category_keywords:
                    if query_lower in kw_info.get('keyword', '').lower():
                        score += 2
                        break
            
            if score > 0:
                article_data['search_score'] = score
                results.append(article_data)
        
        # Sort by relevance score
        results.sort(key=lambda x: x['search_score'], reverse=True)
        
        return results[:limit]
    
    def export_articles(self, output_file, format='json', date_range=None):
        """
        Export cached articles to file
        
        Args:
            output_file (str): Output file path
            format (str): Export format ('json', 'csv')
            date_range (tuple): (start_date, end_date) optional
        """
        articles_to_export = list(self.article_cache.values())
        
        # Apply date filtering if specified
        if date_range:
            start_date, end_date = date_range
            filtered_articles = []
            
            for article in articles_to_export:
                try:
                    cached_time = datetime.fromisoformat(article.get('cached_at', ''))
                    if start_date <= cached_time <= end_date:
                        filtered_articles.append(article)
                except (ValueError, TypeError):
                    continue
            
            articles_to_export = filtered_articles
        
        # Export based on format
        if format.lower() == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(articles_to_export, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Exported {len(articles_to_export)} articles to {output_file}")
        
        return len(articles_to_export)
    
    def _generate_article_hash(self, article):
        """Generate unique hash for article"""
        # Use URL + title for unique identification
        url = article.get('url', '')
        title = article.get('title', '')
        
        unique_string = f"{url}|{title}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()
    
    def _prepare_article_for_cache(self, article):
        """Prepare article data for caching"""
        cached_article = dict(article)  # Copy
        
        # Add cache metadata
        cached_article['cached_at'] = datetime.now().isoformat()
        cached_article['cache_version'] = '2.0'
        
        # Ensure required fields exist
        required_fields = ['title', 'url', 'source', 'published']
        for field in required_fields:
            if field not in cached_article:
                cached_article[field] = ''
        
        return cached_article
    
    def _should_update_cached_article(self, new_article, cached_article):
        """Determine if cached article should be updated"""
        # Update if new article has more content
        new_content_length = len(new_article.get('content', ''))
        cached_content_length = len(cached_article.get('content', ''))
        
        if new_content_length > cached_content_length:
            return True
        
        # Update if new article has relevance scores and cached doesn't
        if ('relevance_score' in new_article and 
            'relevance_score' not in cached_article):
            return True
        
        return False
    
    def _update_source_stats(self, source_name, article_count):
        """Update statistics for a source"""
        if not source_name:
            return
        
        if 'sources_stats' not in self.metadata:
            self.metadata['sources_stats'] = {}
        
        source_stats = self.metadata['sources_stats'].get(source_name, {
            'total_articles': 0,
            'last_update': None,
            'fetch_count': 0
        })
        
        source_stats['total_articles'] += article_count
        source_stats['last_update'] = datetime.now().isoformat()
        source_stats['fetch_count'] += 1
        
        self.metadata['sources_stats'][source_name] = source_stats
        self.metadata['last_update'] = datetime.now().isoformat()
    
    def _load_json_file(self, file_path, default=None):
        """Load JSON file with error handling"""
        if default is None:
            default = {}
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, IOError):
            pass
        
        return default
    
    def _save_caches(self):
        """Save all cache files"""
        try:
            # Save article cache
            with open(self.article_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.article_cache, f, indent=2, ensure_ascii=False)
            
            # Save metadata
            with open(self.metadata_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"   ⚠️  Error saving cache: {e}")
    
    def _get_cache_size_mb(self):
        """Calculate total cache size in MB"""
        total_size = 0
        
        for cache_file in [self.article_cache_file, self.metadata_cache_file]:
            try:
                if cache_file.exists():
                    total_size += cache_file.stat().st_size
            except OSError:
                continue
        
        return round(total_size / (1024 * 1024), 2)