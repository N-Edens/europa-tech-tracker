"""
Pytest configuration and shared fixtures for Europa Tech Tracker tests.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pytest
import yaml
from unittest.mock import MagicMock

# Test data fixtures
@pytest.fixture
def sample_rss_feed():
    """Sample RSS feed content for testing"""
    return """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>European Tech News</title>
        <description>Latest European technology news</description>
        <link>https://example.com</link>
        <lastBuildDate>Mon, 11 Mar 2026 10:00:00 GMT</lastBuildDate>
        
        <item>
            <title>Danish Fintech Startup Raises €10M Series A</title>
            <description>Copenhagen-based fintech company secures funding from European VCs to expand across Nordic region</description>
            <link>https://example.com/danish-fintech-funding</link>
            <pubDate>Mon, 11 Mar 2026 09:30:00 GMT</pubDate>
            <guid>1001</guid>
        </item>
        
        <item>
            <title>Berlin AI Company Partners with SAP</title>
            <description>German artificial intelligence startup announces strategic partnership with SAP to develop enterprise solutions</description>
            <link>https://example.com/berlin-ai-sap</link>
            <pubDate>Mon, 11 Mar 2026 08:45:00 GMT</pubDate>
            <guid>1002</guid>
        </item>
        
        <item>
            <title>Silicon Valley Giant Acquires European Rival</title>
            <description>US tech company announces acquisition of London-based competitor for $2B</description>
            <link>https://example.com/us-acquisition</link>
            <pubDate>Sun, 10 Mar 2026 15:20:00 GMT</pubDate>
            <guid>1003</guid>
        </item>
        
        <item>
            <title>French Cloud Provider Launches New Data Centers</title>
            <description>OVHcloud expands infrastructure with three new data centers across France and Germany</description>
            <link>https://example.com/ovh-datacenter</link>
            <pubDate>Sun, 10 Mar 2026 12:15:00 GMT</pubDate>
            <guid>1004</guid>
        </item>
    </channel>
</rss>"""

@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        'sources': {
            'tech_eu': {
                'url': 'https://tech.eu/feed/',
                'active': True,
                'rate_limit': 1.0,
                'timeout': 30
            },
            'test_source': {
                'url': 'https://example.com/feed.xml',
                'active': True,
                'rate_limit': 0.5,
                'timeout': 15
            }
        },
        'keywords': {
            'companies': {
                'high_priority': ['SAP', 'ASML', 'Nokia', 'Ericsson'],
                'medium_priority': ['fintech', 'startup', 'European', 'Nordic']
            },
            'technology': {
                'high_priority': ['artificial intelligence', 'blockchain', 'quantum'],
                'medium_priority': ['cloud computing', 'cybersecurity', 'IoT']
            }
        },
        'settings': {
            'cache_max_age_days': 7,
            'article_max_age_hours': 48,
            'similarity_threshold': 0.8,
            'relevance_threshold': 10.0
        }
    }

@pytest.fixture
def sample_articles():
    """Sample articles for testing processing pipeline"""
    base_time = datetime(2026, 3, 11, 10, 0, 0)
    
    return [
        {
            'title': 'Danish Fintech Startup Raises €10M Series A',
            'link': 'https://example.com/danish-fintech-funding',
            'description': 'Copenhagen-based fintech company secures funding from European VCs',
            'published': base_time.isoformat(),
            'source': 'tech_eu',
            'guid': '1001'
        },
        {
            'title': 'Berlin AI Company Partners with SAP',
            'link': 'https://example.com/berlin-ai-sap', 
            'description': 'German AI startup announces strategic partnership with SAP',
            'published': (base_time - timedelta(minutes=45)).isoformat(),
            'source': 'tech_eu',
            'guid': '1002'
        },
        {
            'title': 'French Cloud Provider Launches New Data Centers',
            'link': 'https://example.com/ovh-datacenter',
            'description': 'OVHcloud expands infrastructure with new data centers',
            'published': (base_time - timedelta(hours=2)).isoformat(), 
            'source': 'ovh_news',
            'guid': '1004'
        }
    ]

@pytest.fixture
def processed_articles():
    """Sample processed articles with scoring and metadata"""
    return [
        {
            'title': 'Danish Fintech Startup Raises €10M Series A',
            'link': 'https://example.com/danish-fintech-funding',
            'description': 'Copenhagen-based fintech company secures funding from European VCs',
            'published': '2026-03-11T10:00:00',
            'source': 'tech_eu',
            'guid': '1001',
            'relevance_score': 18.5,
            'primary_category': 'startup_funding',
            'matched_keywords': {
                'companies': [
                    {'keyword': 'fintech', 'occurrences': 2, 'priority': 'medium'},
                    {'keyword': 'European', 'occurrences': 1, 'priority': 'medium'}
                ]
            },
            'cached_at': '2026-03-11T10:30:00',
            'content_hash': 'abc123def456'
        },
        {
            'title': 'Berlin AI Company Partners with SAP',
            'link': 'https://example.com/berlin-ai-sap',
            'description': 'German AI startup announces strategic partnership with SAP',
            'published': '2026-03-11T09:15:00',
            'source': 'tech_eu', 
            'guid': '1002',
            'relevance_score': 22.1,
            'primary_category': 'partnerships',
            'matched_keywords': {
                'companies': [
                    {'keyword': 'SAP', 'occurrences': 1, 'priority': 'high'}
                ],
                'technology': [
                    {'keyword': 'artificial intelligence', 'occurrences': 1, 'priority': 'high'}
                ]
            },
            'cached_at': '2026-03-11T10:30:00',
            'content_hash': 'def456ghi789'
        }
    ]

@pytest.fixture
def temp_directories():
    """Create temporary directories for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create directory structure
        (temp_path / 'data' / 'cache').mkdir(parents=True)
        (temp_path / 'output' / 'daily_reports').mkdir(parents=True)
        (temp_path / 'output' / 'weekly_summaries').mkdir(parents=True)
        (temp_path / 'logs').mkdir(parents=True)
        (temp_path / 'config').mkdir(parents=True)
        
        yield {
            'root': temp_path,
            'cache': temp_path / 'data' / 'cache',
            'output': temp_path / 'output',
            'logs': temp_path / 'logs',
            'config': temp_path / 'config'
        }

@pytest.fixture
def mock_cache_file(temp_directories, processed_articles):
    """Create a mock cache file for testing"""
    cache_file = temp_directories['cache'] / 'article_cache.json'
    
    cache_data = {}
    for i, article in enumerate(processed_articles):
        cache_data[f"key_{i}"] = article
        
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)
        
    return cache_file

@pytest.fixture
def mock_config_file(temp_directories, sample_config):
    """Create a mock config file for testing"""
    config_file = temp_directories['config'] / 'sources.yaml'
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f, default_flow_style=False)
        
    return config_file

@pytest.fixture
def mock_requests():
    """Mock requests for RSS feed testing"""
    import responses
    
    with responses.RequestsMock() as rsps:
        yield rsps

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    return MagicMock()


# Test categories
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests") 
    config.addinivalue_line("markers", "workflow: Workflow tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "network: Tests requiring internet")


# Custom assertions
def assert_valid_article_structure(article: Dict[str, Any]):
    """Assert that article has required structure"""
    required_fields = ['title', 'link', 'description', 'published', 'source', 'guid']
    for field in required_fields:
        assert field in article, f"Article missing required field: {field}"
        assert article[field], f"Article field {field} is empty"

def assert_valid_processed_article(article: Dict[str, Any]):
    """Assert that processed article has required metadata"""
    assert_valid_article_structure(article)
    
    required_processed_fields = [
        'relevance_score', 'primary_category', 'matched_keywords',
        'cached_at', 'content_hash'
    ]
    
    for field in required_processed_fields:
        assert field in article, f"Processed article missing field: {field}"
        
    # Validate score range
    assert 0 <= article['relevance_score'] <= 30, "Relevance score out of range"
    
    # Validate keywords structure
    assert isinstance(article['matched_keywords'], dict), "matched_keywords must be dict"

def assert_valid_cache_entry(cache_entry: Dict[str, Any]):
    """Assert that cache entry is properly formatted"""
    assert_valid_processed_article(cache_entry)
    
    # Validate timestamps
    try:
        datetime.fromisoformat(cache_entry['cached_at'])
        datetime.fromisoformat(cache_entry['published'])
    except ValueError as e:
        pytest.fail(f"Invalid timestamp format: {e}")


# Test utilities
class MockRSSFeed:
    """Mock RSS feed for testing"""
    
    def __init__(self, feed_content: str):
        self.content = feed_content
        self.status_code = 200
        
    def text(self):
        return self.content