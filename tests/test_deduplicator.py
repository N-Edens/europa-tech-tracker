"""
Unit tests for Article Deduplicator utility  
Tests Phase 2 functionality: similarity detection, content deduplication
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.deduplicator import ArticleDeduplicator


@pytest.mark.unit
class TestArticleDeduplicator:
    """Test cases for ArticleDeduplicator functionality"""
    
    def test_deduplicator_initialization(self):
        """Test deduplicator initialization with default parameters"""
        deduplicator = ArticleDeduplicator()
        
        assert deduplicator.similarity_threshold == 0.8
        assert isinstance(deduplicator.seen_articles, dict)
        assert len(deduplicator.seen_articles) == 0
        
    def test_deduplicator_custom_threshold(self):
        """Test initialization with custom similarity threshold"""
        threshold = 0.9
        deduplicator = ArticleDeduplicator(similarity_threshold=threshold)
        
        assert deduplicator.similarity_threshold == threshold
        
    def test_normalize_text_basic(self):
        """Test basic text normalization"""
        deduplicator = ArticleDeduplicator()
        
        text = "This is a Test Article with SPECIAL characters! 123"
        normalized = deduplicator._normalize_text(text)
        
        assert normalized == "this is a test article with special characters"
        assert "123" not in normalized
        assert "!" not in normalized
        
    def test_normalize_text_edge_cases(self):
        """Test text normalization with edge cases"""
        deduplicator = ArticleDeduplicator()
        
        # Empty string
        assert deduplicator._normalize_text("") == ""
        
        # Special characters and whitespace
        text = "   Multiple    Spaces\t\nAnd\r\nTabs   "
        normalized = deduplicator._normalize_text(text)
        assert normalized == "multiple spaces and tabs"
        
        # Numbers and symbols
        text = "Article $100M €50K #hashtag @mention"
        normalized = deduplicator._normalize_text(text)
        assert normalized == "article m k hashtag mention"
        
    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical content"""
        deduplicator = ArticleDeduplicator()
        
        article1 = {
            'title': 'Identical Article Title',
            'description': 'This is exactly the same description content'
        }
        
        article2 = article1.copy()
        
        similarity = deduplicator._calculate_similarity(article1, article2)
        assert similarity == 1.0
        
    def test_calculate_similarity_different(self):
        """Test similarity calculation for completely different content"""
        deduplicator = ArticleDeduplicator()
        
        article1 = {
            'title': 'European Fintech Raises Funding',
            'description': 'A Copenhagen-based fintech company secured Series A funding'
        }
        
        article2 = {
            'title': 'Berlin AI Startup Launches Product',
            'description': 'German artificial intelligence company releases enterprise solution'
        }
        
        similarity = deduplicator._calculate_similarity(article1, article2)
        assert 0.0 <= similarity <= 1.0
        assert similarity < 0.5  # Should be quite different
        
    def test_calculate_similarity_partial(self):
        """Test similarity calculation for partially similar content"""
        deduplicator = ArticleDeduplicator()
        
        article1 = {
            'title': 'Danish Fintech Company Raises Series A Funding',
            'description': 'Copenhagen fintech secures €10M in Series A round'
        }
        
        article2 = {
            'title': 'Danish Fintech Startup Gets Series A Investment',
            'description': 'Copenhagen-based fintech company raises €10M Series A'
        }
        
        similarity = deduplicator._calculate_similarity(article1, article2)
        assert 0.5 < similarity < 1.0  # Should be similar but not identical
        
    def test_is_duplicate_above_threshold(self):
        """Test duplicate detection when similarity is above threshold"""
        deduplicator = ArticleDeduplicator(similarity_threshold=0.8)
        
        # Add first article
        article1 = {
            'title': 'Berlin AI Company Partners with SAP',
            'description': 'German startup announces strategic partnership',
            'link': 'https://example.com/article1',
            'guid': 'guid1'
        }
        
        deduplicator.add_article(article1)
        
        # Test very similar article (should be duplicate)
        article2 = {
            'title': 'Berlin AI Startup Partners with SAP',
            'description': 'German AI company announces strategic partnership',
            'link': 'https://example.com/article2',
            'guid': 'guid2'
        }
        
        is_duplicate, similarity, original = deduplicator.is_duplicate(article2)
        
        assert is_duplicate
        assert similarity > 0.8
        assert original['guid'] == 'guid1'
        
    def test_is_duplicate_below_threshold(self):
        """Test duplicate detection when similarity is below threshold"""
        deduplicator = ArticleDeduplicator(similarity_threshold=0.8)
        
        # Add first article
        article1 = {
            'title': 'European Fintech News',
            'description': 'Financial technology developments in Europe',
            'link': 'https://example.com/article1',
            'guid': 'guid1'
        }
        
        deduplicator.add_article(article1)
        
        # Test different article (should not be duplicate)
        article2 = {
            'title': 'Berlin AI Product Launch',
            'description': 'Artificial intelligence company releases new product',
            'link': 'https://example.com/article2', 
            'guid': 'guid2'
        }
        
        is_duplicate, similarity, original = deduplicator.is_duplicate(article2)
        
        assert not is_duplicate
        assert similarity < 0.8
        assert original is None
        
    def test_add_article_success(self):
        """Test successfully adding new article to deduplicator"""
        deduplicator = ArticleDeduplicator()
        
        article = {
            'title': 'New Article Title',
            'description': 'Article description content',
            'link': 'https://example.com/new-article',
            'guid': 'new_guid'
        }
        
        deduplicator.add_article(article)
        
        # Verify article was added
        assert len(deduplicator.seen_articles) == 1
        
        # Article should now be detected as duplicate if added again
        is_duplicate, _, _ = deduplicator.is_duplicate(article)
        assert is_duplicate
        
    def test_add_article_duplicate(self):
        """Test adding duplicate article"""
        deduplicator = ArticleDeduplicator(similarity_threshold=0.8)
        
        article1 = {
            'title': 'Original Article',
            'description': 'Original content description',
            'link': 'https://example.com/original',
            'guid': 'original_guid'
        }
        
        article2 = {
            'title': 'Very Similar Article',
            'description': 'Original content description',  # Same description
            'link': 'https://example.com/similar',
            'guid': 'similar_guid'
        }
        
        # Add first article
        deduplicator.add_article(article1)
        assert len(deduplicator.seen_articles) == 1
        
        # Try to add similar article
        deduplicator.add_article(article2)
        assert len(deduplicator.seen_articles) == 1  # Should still be 1
        
    def test_clear_deduplicator(self):
        """Test clearing the deduplicator state"""
        deduplicator = ArticleDeduplicator()
        
        # Add some articles
        for i in range(3):
            article = {
                'title': f'Article {i}',
                'description': f'Description {i}',
                'link': f'https://example.com/article{i}',
                'guid': f'guid{i}'
            }
            deduplicator.add_article(article)
            
        assert len(deduplicator.seen_articles) == 3
        
        # Clear state
        deduplicator.clear()
        assert len(deduplicator.seen_articles) == 0
        
    def test_get_duplicate_stats(self):
        """Test statistics generation for duplicate detection"""
        deduplicator = ArticleDeduplicator()
        
        # Add original articles
        article1 = {
            'title': 'First Article',
            'description': 'First description',
            'link': 'https://example.com/first',
            'guid': 'first_guid'
        }
        
        article2 = {
            'title': 'Second Article', 
            'description': 'Second description',
            'link': 'https://example.com/second',
            'guid': 'second_guid'
        }
        
        deduplicator.add_article(article1)
        deduplicator.add_article(article2)
        
        # Try to add duplicate
        duplicate_article = {
            'title': 'First Article Copy',
            'description': 'First description',  # Same as first
            'link': 'https://example.com/first-copy',
            'guid': 'first_copy_guid'
        }
        
        # This should be detected as duplicate
        is_duplicate, _, _ = deduplicator.is_duplicate(duplicate_article)
        assert is_duplicate
        
        # Get stats
        stats = deduplicator.get_stats()
        
        assert 'unique_articles' in stats
        assert 'total_processed' in stats
        assert 'duplicate_rate' in stats
        
        assert stats['unique_articles'] == 2
        assert stats['total_processed'] >= 2
        
    def test_exact_duplicate_detection(self):
        """Test detection of exact duplicates (same GUID/URL)"""
        deduplicator = ArticleDeduplicator()
        
        article1 = {
            'title': 'Original Article',
            'description': 'Original description',
            'link': 'https://example.com/same-url',
            'guid': 'same_guid'
        }
        
        article2 = {
            'title': 'Different Title',
            'description': 'Different description', 
            'link': 'https://example.com/same-url',  # Same URL
            'guid': 'same_guid'  # Same GUID
        }
        
        deduplicator.add_article(article1)
        
        # Should detect as duplicate due to same URL/GUID
        is_duplicate, similarity, original = deduplicator.is_duplicate(article2)
        
        assert is_duplicate
        assert similarity == 1.0  # Exact match due to same identifiers
        assert original['guid'] == 'same_guid'
        
    def test_edge_case_empty_content(self):
        """Test handling of articles with empty content"""
        deduplicator = ArticleDeduplicator()
        
        article_empty = {
            'title': '',
            'description': '',
            'link': 'https://example.com/empty',
            'guid': 'empty_guid'
        }
        
        article_content = {
            'title': 'Real Article',
            'description': 'Real content here',
            'link': 'https://example.com/real',
            'guid': 'real_guid'
        }
        
        # Should handle empty content gracefully
        deduplicator.add_article(article_empty)
        deduplicator.add_article(article_content)
        
        assert len(deduplicator.seen_articles) == 2
        
    def test_content_hash_consistency(self):
        """Test that content hash generation is consistent"""
        deduplicator = ArticleDeduplicator()
        
        article = {
            'title': 'Consistent Article',
            'description': 'Same content every time',
            'link': 'https://example.com/consistent',
            'guid': 'consistent_guid'
        }
        
        # Calculate hash multiple times
        hash1 = deduplicator._calculate_content_hash(article)
        hash2 = deduplicator._calculate_content_hash(article)
        hash3 = deduplicator._calculate_content_hash(article)
        
        assert hash1 == hash2 == hash3
        assert isinstance(hash1, str)
        assert len(hash1) > 0