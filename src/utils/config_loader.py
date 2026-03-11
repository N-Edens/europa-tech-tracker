"""
Configuration Loader Module for Europa Tech Tracker
Enhanced configuration loading with validation, environment variables, and defaults
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, List
import re


class ConfigurationLoader:
    """Enhanced configuration loader with validation and environment support"""
    
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_cache = {}
        
    def load_sources_config(self, config_file="sources.yaml"):
        """
        Load and validate RSS sources configuration
        
        Args:
            config_file (str): Configuration file name
        
        Returns:
            dict: Validated configuration
        """
        config_path = self.config_dir / config_file
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Validate configuration
            validated_config = self._validate_sources_config(config)
            
            # Apply environment variable overrides
            self._apply_environment_overrides(validated_config)
            
            return validated_config
            
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {config_path}")
            return self._get_default_config()
        except yaml.YAMLError as e:
            print(f"❌ Error parsing configuration: {e}")
            return self._get_default_config()
    
    def get_enabled_sources(self, config):
        """Get only enabled RSS sources from configuration"""
        if 'sources' not in config:
            return {}
        
        enabled_sources = {}
        total_sources = 0
        
        for name, source_config in config['sources'].items():
            total_sources += 1
            
            if source_config.get('enabled', True):
                enabled_sources[name] = source_config
        
        print(f"   📡 Found {len(enabled_sources)}/{total_sources} enabled sources")
        
        return enabled_sources
    
    def get_keywords_by_category(self, config):
        """Extract and organize keywords by category"""
        if 'keywords' not in config:
            return {}
        
        keywords = config['keywords']
        
        # Validate keyword structure
        validated_keywords = {}
        for category, keyword_list in keywords.items():
            if isinstance(keyword_list, list):
                # Filter out empty keywords
                clean_keywords = [kw for kw in keyword_list if isinstance(kw, str) and kw.strip()]
                if clean_keywords:
                    validated_keywords[category] = clean_keywords
        
        return validated_keywords
    
    def get_output_settings(self, config):
        """Get output configuration with defaults"""
        output_config = config.get('output', {})
        
        defaults = {
            'format': 'markdown',
            'max_articles_per_run': 50,
            'include_summary': True
        }
        
        # Merge with defaults
        for key, default_value in defaults.items():
            if key not in output_config:
                output_config[key] = default_value
        
        return output_config
    
    def get_google_docs_config(self, config):
        """Get Google Docs integration configuration"""
        google_config = config.get('google_docs', {})
        
        # Apply environment variables for sensitive data
        if 'GOOGLE_DOC_ID' in os.environ:
            google_config['doc_id'] = os.environ['GOOGLE_DOC_ID']
        
        if 'GOOGLE_CREDENTIALS_JSON' in os.environ:
            google_config['credentials'] = os.environ['GOOGLE_CREDENTIALS_JSON']
        
        # Default settings
        defaults = {
            'enabled': False,
            'update_frequency': 'daily',
            'max_articles_per_update': 30
        }
        
        for key, default_value in defaults.items():
            if key not in google_config:
                google_config[key] = default_value
        
        return google_config
    
    def get_github_config(self, config):
        """Get GitHub integration configuration"""
        github_config = config.get('github', {})
        
        # Apply environment variables
        if 'GITHUB_USERNAME' in os.environ:
            github_config['username'] = os.environ['GITHUB_USERNAME']
        
        if 'GITHUB_REPOSITORY' in os.environ:
            github_config['repository'] = os.environ['GITHUB_REPOSITORY']
        
        return github_config
    
    def validate_source_url(self, url):
        """Validate RSS/feed URL format"""
        if not url:
            return False
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def update_source_status(self, config_file, source_name, enabled=True):
        """
        Update a source's enabled status in configuration
        
        Args:
            config_file (str): Configuration file path
            source_name (str): Source to update
            enabled (bool): New enabled status
        """
        config_path = self.config_dir / config_file
        
        try:
            # Load current config
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Update source status
            if 'sources' in config and source_name in config['sources']:
                config['sources'][source_name]['enabled'] = enabled
                
                # Save updated config
                with open(config_path, 'w', encoding='utf-8') as file:
                    yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
                
                print(f"   ✅ Updated {source_name}: enabled={enabled}")
                return True
            else:
                print(f"   ❌ Source '{source_name}' not found in configuration")
                return False
                
        except Exception as e:
            print(f"   ❌ Error updating configuration: {e}")
            return False
    
    def add_new_source(self, config_file, source_name, source_config):
        """
        Add a new source to configuration
        
        Args:
            config_file (str): Configuration file path
            source_name (str): Source identifier
            source_config (dict): Source configuration
        """
        config_path = self.config_dir / config_file
        
        try:
            # Load current config
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            
            # Validate new source
            if not self.validate_source_url(source_config.get('url')):
                print(f"   ❌ Invalid URL for source '{source_name}'")
                return False
            
            # Add source
            if 'sources' not in config:
                config['sources'] = {}
            
            config['sources'][source_name] = source_config
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
            
            print(f"   ✅ Added new source: {source_name}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error adding source: {e}")
            return False
    
    def _validate_sources_config(self, config):
        """Validate sources configuration structure"""
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Validate sources section
        if 'sources' in config:
            for source_name, source_config in config['sources'].items():
                if not isinstance(source_config, dict):
                    continue
                
                # Validate required fields
                required_fields = ['name', 'url', 'type']
                for field in required_fields:
                    if field not in source_config:
                        print(f"   ⚠️  Source '{source_name}' missing field: {field}")
                
                # Validate URL
                url = source_config.get('url', '')
                if not self.validate_source_url(url):
                    print(f"   ⚠️  Source '{source_name}' has invalid URL: {url}")
                    source_config['enabled'] = False
        
        return config
    
    def _apply_environment_overrides(self, config):
        """Apply environment variable overrides"""
        # Override specific settings from environment
        env_mappings = {
            'MAX_ARTICLES_PER_DAY': ['output', 'max_articles_per_run'],
            'FILTER_SENSITIVITY': ['filter', 'sensitivity'],
            'ENABLE_SENTIMENT': ['processing', 'sentiment_analysis']
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert to appropriate type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)
                
                # Set in config
                self._set_nested_config(config, config_path, value)
    
    def _get_default_config(self):
        """Return default configuration if file not found"""
        return {
            'sources': {
                'tech_eu': {
                    'name': 'Tech.EU',
                    'url': 'https://tech.eu/feed/',
                    'type': 'rss',
                    'priority': 'high',
                    'enabled': True
                }
            },
            'keywords': {
                'european_companies': ['European startup', 'European tech'],
                'companies': ['Revolut', 'Spotify', 'SAP']
            },
            'output': {
                'format': 'markdown',
                'max_articles_per_run': 50,
                'include_summary': True
            }
        }
    
    def _is_float(self, value):
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _set_nested_config(self, config, path, value):
        """Set value at nested config path"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value


# Alias for backward compatibility with tests
ConfigLoader = ConfigurationLoader


# Test compatibility extension for ConfigLoader
class TestCompatibleConfigLoader(ConfigurationLoader):
    """ConfigLoader with test-compatible API"""
    
    def __init__(self, config_path):
        """Initialize with config file path (test compatibility)"""
        if isinstance(config_path, (str, Path)):
            config_path = Path(config_path)
            if config_path.is_file():
                # If it's a file, use the parent as config_dir
                super().__init__(config_path.parent)
                self.config_path = config_path
                self.config = self._load_config_file(config_path)
            else:
                # If it's a directory, use it as config_dir
                super().__init__(config_path)
                self.config_path = config_path / "sources.yaml"
                self.config = self._load_config_file(self.config_path)
        else:
            raise TypeError(f"config_path must be str or Path, got {type(config_path)}")
    
    def _load_config_file(self, config_file):
        """Load configuration from file"""
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            return {}
        except (yaml.YAMLError, FileNotFoundError):
            return {}
    
    def get_sources(self, active_only=True):
        """Get sources configuration (test compatibility)"""
        sources = self.config.get('sources', {})
        
        if active_only:
            return {name: config for name, config in sources.items() 
                   if config.get('active', True)}
        
        return sources
    
    def get_keywords(self, category=None):
        """Get keywords configuration (test compatibility)"""
        keywords = self.config.get('keywords', {})
        
        if category:
            return {category: keywords.get(category, {})} if category in keywords else {}
        
        return keywords
    
    def get_setting(self, key, default=None):
        """Get setting value (test compatibility)"""
        settings = self.config.get('settings', {})
        return settings.get(key, default)
    
    def get_source_config(self, source_name):
        """Get specific source configuration (test compatibility)"""
        sources = self.config.get('sources', {})
        return sources.get(source_name)
    
    def get_keyword_weights(self):
        """Get keyword priority weights (test compatibility)"""
        return {
            'high_priority': 3,
            'medium_priority': 2,
            'low_priority': 1
        }
    
    def reload(self):
        """Reload configuration from file (test compatibility)"""
        self.config = self._load_config_file(self.config_path)


# Override the alias to use the test-compatible version
ConfigLoader = TestCompatibleConfigLoader