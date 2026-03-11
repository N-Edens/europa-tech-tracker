"""
Unit tests for Configuration Loader utility
Tests Phase 1-3 functionality: YAML loading, validation, source management
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.config_loader import ConfigLoader


@pytest.mark.unit
class TestConfigLoader:
    """Test cases for ConfigLoader functionality"""
    
    def test_config_loader_initialization(self, temp_directories):
        """Test ConfigLoader initialization"""
        config_path = temp_directories['config'] / 'sources.yaml'
        config_loader = ConfigLoader(config_path)
        
        assert config_loader.config_path == config_path
        assert config_loader.config == {}
        
    def test_load_valid_config(self, mock_config_file, temp_directories):
        """Test loading valid configuration file"""
        config_loader = ConfigLoader(mock_config_file)
        
        assert config_loader.config is not None
        assert 'sources' in config_loader.config
        assert 'keywords' in config_loader.config
        assert 'settings' in config_loader.config
        
    def test_load_nonexistent_config(self, temp_directories):
        """Test handling of non-existent config file"""
        nonexistent_path = temp_directories['config'] / 'nonexistent.yaml'
        
        with pytest.raises(FileNotFoundError):
            ConfigLoader(nonexistent_path)
            
    @patch('builtins.open', mock_open(read_data="invalid: yaml: content: ["))
    def test_load_invalid_yaml(self, temp_directories):
        """Test handling of invalid YAML content"""
        config_path = temp_directories['config'] / 'invalid.yaml'
        config_path.touch()  # Create empty file
        
        with pytest.raises(yaml.YAMLError):
            ConfigLoader(config_path)
            
    def test_get_sources_all_active(self, mock_config_file):
        """Test retrieving all active sources"""
        config_loader = ConfigLoader(mock_config_file)
        sources = config_loader.get_sources()
        
        # Should return only active sources
        assert len(sources) > 0
        for source_name, source_config in sources.items():
            assert source_config.get('active', True) is True
            assert 'url' in source_config
            
    def test_get_sources_filter_inactive(self, temp_directories, sample_config):
        """Test filtering of inactive sources"""
        # Modify config to have inactive source
        modified_config = sample_config.copy()
        modified_config['sources']['inactive_source'] = {
            'url': 'https://example.com/inactive',
            'active': False,
            'rate_limit': 1.0,
            'timeout': 30
        }
        
        # Save modified config
        config_file = temp_directories['config'] / 'test_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(modified_config, f)
            
        config_loader = ConfigLoader(config_file)
        sources = config_loader.get_sources()
        
        # Should not include inactive source
        assert 'inactive_source' not in sources
        assert 'tech_eu' in sources  # Active source should be included
        
    def test_get_sources_only_active_true(self, temp_directories, sample_config):
        """Test explicitly requesting only active sources"""
        # Add mix of active and inactive sources
        modified_config = sample_config.copy()
        modified_config['sources']['active_source'] = {
            'url': 'https://example.com/active',
            'active': True,
            'rate_limit': 1.0
        }
        modified_config['sources']['inactive_source'] = {
            'url': 'https://example.com/inactive', 
            'active': False,
            'rate_limit': 1.0
        }
        
        config_file = temp_directories['config'] / 'test_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(modified_config, f)
            
        config_loader = ConfigLoader(config_file)
        
        # Test active_only=True (default)
        active_sources = config_loader.get_sources(active_only=True)
        inactive_sources = config_loader.get_sources(active_only=False)
        
        assert 'active_source' in active_sources
        assert 'inactive_source' not in active_sources
        assert 'inactive_source' in inactive_sources
        
    def test_get_keywords_by_category(self, mock_config_file):
        """Test retrieving keywords by category"""
        config_loader = ConfigLoader(mock_config_file)
        
        # Get all keywords
        all_keywords = config_loader.get_keywords()
        assert 'companies' in all_keywords
        assert 'technology' in all_keywords
        
        # Get specific category
        company_keywords = config_loader.get_keywords(category='companies')
        assert 'companies' in company_keywords
        assert 'technology' not in company_keywords
        
        # Get non-existent category
        empty_keywords = config_loader.get_keywords(category='nonexistent')
        assert empty_keywords == {}
        
    def test_get_keywords_with_priority(self, mock_config_file):
        """Test keyword retrieval respects priority levels"""
        config_loader = ConfigLoader(mock_config_file)
        
        company_keywords = config_loader.get_keywords(category='companies')
        
        assert 'high_priority' in company_keywords['companies'] 
        assert 'medium_priority' in company_keywords['companies']
        
        # Check specific keywords exist
        high_priority = company_keywords['companies']['high_priority']
        medium_priority = company_keywords['companies']['medium_priority']
        
        assert 'SAP' in high_priority
        assert 'fintech' in medium_priority
        
    def test_get_setting_default_values(self, mock_config_file):
        """Test setting retrieval with default values"""
        config_loader = ConfigLoader(mock_config_file)
        
        # Existing settings
        cache_max_age = config_loader.get_setting('cache_max_age_days')
        assert cache_max_age == 7
        
        similarity_threshold = config_loader.get_setting('similarity_threshold')
        assert similarity_threshold == 0.8
        
        # Non-existent setting with default
        non_existent = config_loader.get_setting('non_existent_setting', default=42)
        assert non_existent == 42
        
        # Non-existent setting without default
        none_value = config_loader.get_setting('another_non_existent')
        assert none_value is None
        
    def test_validate_config_structure(self, mock_config_file):
        """Test configuration structure validation"""
        config_loader = ConfigLoader(mock_config_file)
        
        # Should have required sections
        assert 'sources' in config_loader.config
        assert 'keywords' in config_loader.config
        assert 'settings' in config_loader.config
        
        # Sources should have required fields
        sources = config_loader.config['sources']
        for source_name, source_config in sources.items():
            assert 'url' in source_config, f"Source {source_name} missing URL"
            assert isinstance(source_config['url'], str)
            
            # Optional fields should have sensible defaults
            active = source_config.get('active', True)
            assert isinstance(active, bool)
            
            rate_limit = source_config.get('rate_limit', 1.0)
            assert isinstance(rate_limit, (int, float))
            assert rate_limit > 0
            
    def test_reload_config(self, temp_directories, sample_config):
        """Test reloading configuration file"""
        config_file = temp_directories['config'] / 'test_reload.yaml'
        
        # Save initial config
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
            
        config_loader = ConfigLoader(config_file)
        initial_sources = len(config_loader.get_sources())
        
        # Modify config file
        sample_config['sources']['new_source'] = {
            'url': 'https://example.com/new',
            'active': True,
            'rate_limit': 2.0
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)
            
        # Reload config
        config_loader.reload()
        updated_sources = len(config_loader.get_sources())
        
        assert updated_sources == initial_sources + 1
        assert 'new_source' in config_loader.get_sources()
        
    def test_source_validation(self, temp_directories):
        """Test validation of source configurations"""
        # Create config with invalid source
        invalid_config = {
            'sources': {
                'valid_source': {
                    'url': 'https://example.com/valid',
                    'active': True,
                    'rate_limit': 1.0,
                    'timeout': 30
                },
                'invalid_source': {
                    'url': 'not-a-valid-url',
                    'active': 'not-boolean',
                    'rate_limit': 'not-number'
                }
            },
            'keywords': {'companies': {}},
            'settings': {}
        }
        
        config_file = temp_directories['config'] / 'invalid_source.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(invalid_config, f)
            
        config_loader = ConfigLoader(config_file)
        
        # Should still load but with validation warnings
        sources = config_loader.get_sources()
        
        # Should include valid source
        assert 'valid_source' in sources
        assert sources['valid_source']['url'] == 'https://example.com/valid'
        
    def test_get_source_config(self, mock_config_file):
        """Test retrieving specific source configuration"""
        config_loader = ConfigLoader(mock_config_file)
        
        # Get existing source
        tech_eu_config = config_loader.get_source_config('tech_eu')
        assert tech_eu_config is not None
        assert tech_eu_config['url'] == 'https://tech.eu/feed/'
        assert tech_eu_config.get('active', True) is True
        
        # Get non-existent source
        non_existent = config_loader.get_source_config('non_existent_source')
        assert non_existent is None
        
    def test_config_file_path_resolution(self):
        """Test proper file path resolution"""
        # Test with string path
        config_loader = ConfigLoader('config/sources.yaml')
        assert isinstance(config_loader.config_path, Path)
        
        # Test with Path object
        path_obj = Path('config/sources.yaml')
        config_loader = ConfigLoader(path_obj)
        assert config_loader.config_path == path_obj
        
    def test_get_keyword_weights(self, mock_config_file):
        """Test keyword priority weight calculation"""
        config_loader = ConfigLoader(mock_config_file)
        
        # Should be able to get numeric weights for priorities
        weights = config_loader.get_keyword_weights()
        
        assert 'high_priority' in weights
        assert 'medium_priority' in weights
        assert weights['high_priority'] > weights['medium_priority']
        
    def test_empty_config_sections(self, temp_directories):
        """Test handling of empty configuration sections"""
        empty_config = {
            'sources': {},
            'keywords': {},
            'settings': {}
        }
        
        config_file = temp_directories['config'] / 'empty_config.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(empty_config, f)
            
        config_loader = ConfigLoader(config_file)
        
        # Should handle empty sections gracefully
        sources = config_loader.get_sources()
        keywords = config_loader.get_keywords()
        
        assert sources == {}
        assert keywords == {}
        
        # Settings should return defaults
        default_setting = config_loader.get_setting('unknown', default='test')
        assert default_setting == 'test'