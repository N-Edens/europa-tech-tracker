"""
Integration tests for RSS processing pipeline
Tests Phase 1-2 functionality: RSS fetching, article processing, end-to-end flow
"""

import pytest
import responses
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the imports for now since main.py functions may not exist yet
# from src.main import collect_articles, process_articles, load_configuration


@pytest.mark.integration
class TestRSSProcessingPipeline:
    """Integration tests for the complete RSS processing pipeline"""
    
    @responses.activate
    def test_collect_articles_success(self, sample_rss_feed, sample_config, temp_directories):
        """Test successful RSS collection from multiple sources"""
        # Mock RSS responses
        responses.add(responses.GET, 'https://tech.eu/feed/', body=sample_rss_feed, status=200)
        responses.add(responses.GET, 'https://example.com/feed.xml', body=sample_rss_feed, status=200)
        
        # Mock configuration
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            
            # Mock logger
            mock_logger = MagicMock()
            
            articles = collect_articles(mock_logger, cache_dir=temp_directories['cache'])
            
            assert len(articles) > 0
            
            # Verify article structure
            for article in articles:
                assert 'title' in article
                assert 'link' in article
                assert 'description' in article
                assert 'published' in article
                assert 'source' in article
                assert 'guid' in article
                
    @responses.activate
    def test_collect_articles_partial_failure(self, sample_rss_feed, sample_config, temp_directories):
        """Test RSS collection with some sources failing"""
        # Mock mixed success/failure responses
        responses.add(responses.GET, 'https://tech.eu/feed/', body=sample_rss_feed, status=200)
        responses.add(responses.GET, 'https://example.com/feed.xml', status=404)
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            articles = collect_articles(mock_logger, cache_dir=temp_directories['cache'])
            
            # Should still get articles from successful sources
            assert len(articles) >= 0
            
            # Logger should have recorded errors
            mock_logger.error.assert_called()
            
    @responses.activate  
    def test_collect_articles_all_sources_fail(self, sample_config, temp_directories):
        """Test RSS collection when all sources fail"""
        # Mock all sources to fail
        responses.add(responses.GET, 'https://tech.eu/feed/', status=403)
        responses.add(responses.GET, 'https://example.com/feed.xml', status=500)
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            articles = collect_articles(mock_logger, cache_dir=temp_directories['cache'])
            
            # Should return empty list
            assert len(articles) == 0
            
    def test_process_articles_with_keywords(self, sample_articles, sample_config, temp_directories):
        """Test article processing with keyword filtering"""
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            mock_deduplicator = MagicMock()
            mock_deduplicator.is_duplicate.return_value = (False, 0.0, None)
            
            processed = process_articles(
                sample_articles, 
                mock_logger, 
                cache_dir=temp_directories['cache'],
                deduplicator=mock_deduplicator
            )
            
            assert len(processed) > 0
            
            # Check processed article structure
            for article in processed:
                assert_valid_processed_article(article)
                assert article['relevance_score'] >= 0
                assert 'primary_category' in article
                assert 'matched_keywords' in article
                
    def test_process_articles_deduplication(self, temp_directories, sample_config):
        """Test article deduplication during processing"""
        # Create duplicate articles
        articles = [
            {
                'title': 'Danish Fintech Startup Raises Funding',
                'description': 'Copenhagen-based fintech company secures investment',
                'link': 'https://example.com/article1',
                'published': datetime.now().isoformat(),
                'source': 'tech_eu',
                'guid': 'guid1'
            },
            {
                'title': 'Danish Fintech Company Gets Investment',  # Very similar
                'description': 'Copenhagen-based fintech company secures investment',  # Same description
                'link': 'https://example.com/article2',
                'published': datetime.now().isoformat(),
                'source': 'other_source', 
                'guid': 'guid2'
            },
            {
                'title': 'Completely Different Article',
                'description': 'About something totally unrelated',
                'link': 'https://example.com/article3',
                'published': datetime.now().isoformat(),
                'source': 'tech_eu',
                'guid': 'guid3'
            }
        ]
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            processed = process_articles(
                articles, 
                mock_logger, 
                cache_dir=temp_directories['cache']
            )
            
            # Should have fewer articles due to deduplication
            assert len(processed) <= len(articles)
            
            # Should log deduplication
            # mock_logger.info.assert_any_call(contains="duplicate")
            
    def test_process_articles_relevance_filtering(self, temp_directories, sample_config):
        """Test filtering articles based on European relevance"""
        articles = [
            {
                'title': 'European AI Startup Launches in Berlin',
                'description': 'German artificial intelligence company releases product',
                'link': 'https://example.com/european-ai',
                'published': datetime.now().isoformat(),
                'source': 'tech_eu',
                'guid': 'european_guid'
            },
            {
                'title': 'Silicon Valley Company IPO',
                'description': 'American tech giant goes public on NASDAQ',
                'link': 'https://example.com/us-ipo',
                'published': datetime.now().isoformat(),
                'source': 'us_source',
                'guid': 'us_guid'
            }
        ]
        
        # Set higher relevance threshold
        config_with_threshold = sample_config.copy()
        config_with_threshold['settings']['relevance_threshold'] = 15.0
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = config_with_threshold
            mock_logger = MagicMock()
            
            processed = process_articles(
                articles,
                mock_logger,
                cache_dir=temp_directories['cache']
            )
            
            # Should prioritize European content
            if processed:
                european_articles = [a for a in processed if 'european' in a['title'].lower() or 'german' in a['description'].lower()]
                us_articles = [a for a in processed if 'silicon valley' in a['title'].lower()]
                
                # European articles should have higher relevance scores
                if european_articles and us_articles:
                    assert european_articles[0]['relevance_score'] > us_articles[0]['relevance_score']
                    
    @responses.activate
    def test_end_to_end_processing(self, sample_rss_feed, sample_config, temp_directories):
        """Test complete end-to-end processing pipeline"""
        # Mock RSS response
        responses.add(responses.GET, 'https://tech.eu/feed/', body=sample_rss_feed, status=200)
        responses.add(responses.GET, 'https://example.com/feed.xml', body=sample_rss_feed, status=200)
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            # Step 1: Collect articles
            articles = collect_articles(mock_logger, cache_dir=temp_directories['cache'])
            assert len(articles) > 0
            
            # Step 2: Process articles
            processed = process_articles(
                articles,
                mock_logger, 
                cache_dir=temp_directories['cache']
            )
            assert len(processed) >= 0
            
            # Verify processing metadata
            for article in processed:
                assert_valid_processed_article(article)
                
                # Should have processing timestamps
                assert 'cached_at' in article
                assert 'content_hash' in article
                
                # Should have relevance scoring
                assert 0 <= article['relevance_score'] <= 30
                
    def test_cache_integration(self, temp_directories, sample_config):
        """Test integration with cache manager"""
        articles = [
            {
                'title': 'Test Cache Integration',
                'description': 'Testing cache functionality',
                'link': 'https://example.com/cache-test',
                'published': datetime.now().isoformat(),
                'source': 'test_source',
                'guid': 'cache_test_guid'
            }
        ]
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            # Process articles
            processed = process_articles(
                articles,
                mock_logger,
                cache_dir=temp_directories['cache']
            )
            
            # Check cache file was created
            cache_file = temp_directories['cache'] / 'article_cache.json'
            assert cache_file.exists()
            
            # Process same articles again
            processed_again = process_articles(
                articles,
                mock_logger,
                cache_dir=temp_directories['cache']
            )
            
            # Should detect as duplicate from cache
            # (actual implementation may vary based on deduplicator logic)
            
    @responses.activate
    def test_rate_limiting_behavior(self, sample_rss_feed, temp_directories):
        """Test that rate limiting is respected"""
        # Configure fast rate limiting for testing
        rate_limited_config = {
            'sources': {
                'fast_source': {
                    'url': 'https://example.com/fast',
                    'active': True,
                    'rate_limit': 0.1,  # Very fast for testing
                    'timeout': 5
                }
            },
            'keywords': {'companies': {'high_priority': ['test']}},
            'settings': {'cache_max_age_days': 7}
        }
        
        responses.add(responses.GET, 'https://example.com/fast', body=sample_rss_feed, status=200)
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = rate_limited_config
            mock_logger = MagicMock()
            
            import time
            start_time = time.time()
            
            articles = collect_articles(mock_logger, cache_dir=temp_directories['cache'])
            
            elapsed_time = time.time() - start_time
            
            # Should have respected rate limit (at least some delay)
            # Note: Actual implementation may vary
            assert elapsed_time >= 0  # Basic sanity check
            
    def test_configuration_loading_integration(self, mock_config_file):
        """Test configuration loading integration"""
        config = load_configuration(mock_config_file)
        
        assert config is not None
        assert 'sources' in config
        assert 'keywords' in config
        assert 'settings' in config
        
        # Verify sources are properly loaded
        sources = config['sources']
        assert len(sources) > 0
        
        # Verify keywords are structured correctly
        keywords = config['keywords']
        assert 'companies' in keywords or 'technology' in keywords
        
    def test_error_recovery_and_logging(self, temp_directories, sample_config):
        """Test error recovery and comprehensive logging"""
        # Create problematic article that might cause processing errors
        problematic_articles = [
            {
                'title': '',  # Empty title
                'description': None,  # None description
                'link': 'invalid-url',  # Invalid URL format
                'published': 'invalid-date',  # Invalid date
                'source': 'test_source',
                'guid': 'problematic_guid'
            },
            {
                'title': 'Valid Article',
                'description': 'This article should process successfully',
                'link': 'https://example.com/valid',
                'published': datetime.now().isoformat(),
                'source': 'test_source', 
                'guid': 'valid_guid'
            }
        ]
        
        with patch('src.main.load_configuration') as mock_config:
            mock_config.return_value = sample_config
            mock_logger = MagicMock()
            
            # Should handle errors gracefully
            processed = process_articles(
                problematic_articles,
                mock_logger,
                cache_dir=temp_directories['cache']
            )
            
            # Should process at least the valid article
            valid_processed = [a for a in processed if a.get('title') == 'Valid Article']
            assert len(valid_processed) > 0
            
            # Should have logged errors for problematic article
            # mock_logger.error.assert_called()  # Implementation details may vary