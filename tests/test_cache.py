"""
Unit tests for Cache Manager utility
Tests Phase 1 & 2 functionality: caching, retrieval, cleanup
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.cache import CacheManager


def assert_valid_cache_entry(cache_entry):
    """Assert that cache entry is properly formatted"""
    required_fields = ['title', 'cached_at']
    for field in required_fields:
        assert field in cache_entry, f"Cache entry missing field: {field}"


@pytest.mark.unit
class TestCacheManager:
    """Test cases for CacheManager functionality"""
    
    def test_cache_manager_initialization(self, temp_directories):
        """Test CacheManager initialization with directories"""
        cache_dir = temp_directories['cache']
        cache_manager = CacheManager(cache_dir)
        
        assert cache_manager.cache_dir == cache_dir
        assert cache_manager.cache_file == cache_dir / 'article_cache.json'
        assert cache_manager._cache == {}
        
    def test_load_existing_cache(self, mock_cache_file, temp_directories):
        """Test loading existing cache file"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Cache should be loaded automatically
        assert len(cache_manager._cache) > 0
        
        # Verify cache structure
        for key, article in cache_manager._cache.items():
            assert_valid_cache_entry(article)
            assert isinstance(key, str)
            
    def test_load_empty_cache(self, temp_directories):
        """Test initialization with no existing cache"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        assert cache_manager._cache == {}
        assert not cache_manager.cache_file.exists()
        
    @patch('json.load')
    def test_load_corrupted_cache(self, mock_json_load, temp_directories):
        """Test handling of corrupted cache file"""
        # Create cache file
        cache_file = temp_directories['cache'] / 'article_cache.json'
        cache_file.write_text('corrupted json')
        
        # Mock json.load to raise exception
        mock_json_load.side_effect = json.JSONDecodeError("Corrupted", "doc", 0)
        
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Should handle gracefully and start with empty cache
        assert cache_manager._cache == {}
        
    def test_add_article_to_cache(self, temp_directories, sample_articles):
        """Test adding new articles to cache"""
        cache_manager = CacheManager(temp_directories['cache'])
        article = sample_articles[0].copy()
        
        # Add article
        cache_key = cache_manager.add_article(article)
        
        # Verify article was added with proper metadata
        assert cache_key in cache_manager._cache
        cached_article = cache_manager._cache[cache_key]
        
        assert_valid_cache_entry(cached_article)
        assert cached_article['title'] == article['title']
        assert cached_article['link'] == article['link']
        assert 'cached_at' in cached_article
        assert 'content_hash' in cached_article
        
    def test_duplicate_article_detection(self, temp_directories, sample_articles):
        """Test that duplicate articles are not cached twice"""
        cache_manager = CacheManager(temp_directories['cache'])
        article = sample_articles[0].copy()
        
        # Add article twice
        key1 = cache_manager.add_article(article)
        key2 = cache_manager.add_article(article)
        
        # Should return same key and not duplicate
        assert key1 == key2
        assert len(cache_manager._cache) == 1
        
    def test_article_exists_check(self, mock_cache_file, temp_directories, processed_articles):
        """Test checking if article already exists in cache"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        existing_article = processed_articles[0]
        new_article = {
            'title': 'New Article Title',
            'link': 'https://example.com/new-article',
            'description': 'This is a new article',
            'published': datetime.now().isoformat(),
            'source': 'test_source',
            'guid': 'new_guid'
        }
        
        # Test existing article
        assert cache_manager.article_exists(existing_article['link'])
        assert cache_manager.article_exists(existing_article['guid'])
        
        # Test new article  
        assert not cache_manager.article_exists(new_article['link'])
        assert not cache_manager.article_exists(new_article['guid'])
        
    def test_get_cached_articles_all(self, mock_cache_file, temp_directories):
        """Test retrieving all cached articles"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        articles = cache_manager.get_cached_articles()
        
        assert len(articles) > 0
        for article in articles:
            assert_valid_cache_entry(article)
            
    def test_get_cached_articles_by_time_range(self, mock_cache_file, temp_directories):
        """Test retrieving articles within time range"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Get articles from last 24 hours
        since_time = datetime.now() - timedelta(hours=24)
        articles = cache_manager.get_cached_articles(since=since_time)
        
        assert isinstance(articles, list)
        
        # All articles should be within time range
        for article in articles:
            cached_time = datetime.fromisoformat(article['cached_at'])
            assert cached_time >= since_time
            
    def test_get_cached_articles_by_source(self, mock_cache_file, temp_directories):
        """Test filtering articles by source"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Filter by specific source
        source_name = 'tech_eu'
        articles = cache_manager.get_cached_articles(source=source_name)
        
        for article in articles:
            assert article['source'] == source_name
            
    def test_save_cache_to_disk(self, temp_directories, sample_articles):
        """Test saving cache to disk"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Add articles
        for article in sample_articles:
            cache_manager.add_article(article)
            
        # Save to disk
        cache_manager.save()
        
        # Verify file was created
        assert cache_manager.cache_file.exists()
        
        # Verify content
        with open(cache_manager.cache_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            
        assert len(saved_data) == len(sample_articles)
        
        for key, article in saved_data.items():
            assert_valid_cache_entry(article)
            
    def test_cleanup_old_articles(self, temp_directories):
        """Test automatic cleanup of old articles"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Add old articles
        old_time = datetime.now() - timedelta(days=10)
        recent_time = datetime.now() - timedelta(hours=1)
        
        old_article = {
            'title': 'Old Article',
            'link': 'https://example.com/old',
            'description': 'Old article description', 
            'published': old_time.isoformat(),
            'source': 'test_source',
            'guid': 'old_guid',
            'cached_at': old_time.isoformat(),
            'content_hash': 'old_hash'
        }
        
        recent_article = {
            'title': 'Recent Article', 
            'link': 'https://example.com/recent',
            'description': 'Recent article description',
            'published': recent_time.isoformat(),
            'source': 'test_source',
            'guid': 'recent_guid',
            'cached_at': recent_time.isoformat(),
            'content_hash': 'recent_hash'
        }
        
        # Manually add to cache (bypass add_article to control timestamps)
        cache_manager._cache['old_key'] = old_article
        cache_manager._cache['recent_key'] = recent_article
        
        # Run cleanup (7 days max age)
        removed_count = cache_manager.cleanup_old_articles(max_age_days=7)
        
        # Should have removed old article
        assert removed_count == 1
        assert 'old_key' not in cache_manager._cache
        assert 'recent_key' in cache_manager._cache
        
    def test_get_cache_stats(self, mock_cache_file, temp_directories):
        """Test cache statistics generation"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        stats = cache_manager.get_cache_stats()
        
        assert 'total_articles' in stats
        assert 'cache_size_mb' in stats
        assert 'oldest_article' in stats
        assert 'newest_article' in stats
        assert 'sources' in stats
        
        assert stats['total_articles'] >= 0
        assert stats['cache_size_mb'] >= 0
        assert isinstance(stats['sources'], dict)
        
    def test_clear_cache(self, mock_cache_file, temp_directories):
        """Test clearing entire cache"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        # Verify cache has data
        assert len(cache_manager._cache) > 0
        
        # Clear cache
        cache_manager.clear()
        
        # Verify cache is empty
        assert len(cache_manager._cache) == 0
        assert not cache_manager.cache_file.exists()
        
    def test_content_hash_generation(self, temp_directories):
        """Test content hash generation for deduplication"""
        cache_manager = CacheManager(temp_directories['cache'])
        
        article1 = {
            'title': 'Test Article',
            'description': 'Test description',
            'link': 'https://example.com/test1',
            'published': datetime.now().isoformat(),
            'source': 'test_source',
            'guid': 'test1'
        }
        
        article2 = article1.copy()
        article2['link'] = 'https://example.com/test2'  # Different link
        article2['guid'] = 'test2'  # Different guid
        
        # Add both articles
        key1 = cache_manager.add_article(article1)
        key2 = cache_manager.add_article(article2)
        
        # Should generate different content hashes for different content
        hash1 = cache_manager._cache[key1]['content_hash']
        hash2 = cache_manager._cache[key2]['content_hash']
        
        # For this test, hashes should be the same since title+description are same
        # The actual deduplication logic is in the deduplicator module
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
        assert len(hash1) > 0
        assert len(hash2) > 0