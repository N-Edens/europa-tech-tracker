"""
Logging Module for Europa Tech Tracker
Enhanced logging for GitHub Actions automation and local development
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import json


class EuropaLogger:
    """Enhanced logger for Europa Tech Tracker with GitHub Actions support"""
    
    def __init__(self, name="europa_tech", log_level=None, log_dir="logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Determine log level
        if log_level is None:
            if os.getenv('DEBUG_MODE', 'false').lower() == 'true':
                log_level = logging.DEBUG
            elif os.getenv('GITHUB_ACTION', 'false').lower() == 'true':
                log_level = logging.INFO
            else:
                log_level = logging.INFO
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()  # Clear existing handlers
        
        # Create formatters
        self.console_formatter = self._create_console_formatter()
        self.file_formatter = self._create_file_formatter()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        
        # Track session stats
        self.session_stats = {
            'start_time': datetime.now(),
            'errors': 0,
            'warnings': 0,
            'articles_processed': 0,
            'sources_processed': 0
        }
        
    def _create_console_formatter(self):
        """Create formatter for console output (emoji-friendly for GitHub Actions)"""
        if os.getenv('GITHUB_ACTION', 'false').lower() == 'true':
            # GitHub Actions friendly format
            return logging.Formatter(
                '%(levelname_emoji)s %(message)s',
                defaults={'levelname_emoji': self._get_level_emoji}
            )
        else:
            # Local development format
            return logging.Formatter(
                '%(asctime)s %(levelname_emoji)s %(message)s',
                datefmt='%H:%M:%S',
                defaults={'levelname_emoji': self._get_level_emoji}
            )
    
    def _create_file_formatter(self):
        """Create formatter for file logging"""
        return logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _get_level_emoji(self, record):
        """Get emoji for log level"""
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': '📝',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        return emoji_map.get(record.levelname, '📝')
    
    def _setup_console_handler(self):
        """Setup console output handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.logger.level)
        console_handler.setFormatter(self.console_formatter)
        
        # Custom filter to add emoji
        def add_emoji_filter(record):
            record.levelname_emoji = self._get_level_emoji(record)
            return True
            
        console_handler.addFilter(add_emoji_filter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging handler"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"europa_tech_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_handler.setFormatter(self.file_formatter)
        
        self.logger.addHandler(file_handler)
        self.log_file = log_file
        
    def info(self, message, **kwargs):
        """Log info message with optional stats tracking"""
        self.logger.info(message)
        self._update_stats('info', **kwargs)
        
    def debug(self, message, **kwargs):
        """Log debug message"""
        self.logger.debug(message)
        
    def warning(self, message, **kwargs):
        """Log warning message"""
        self.logger.warning(message)
        self.session_stats['warnings'] += 1
        self._update_stats('warning', **kwargs)
        
    def error(self, message, exception=None, **kwargs):
        """Log error message with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}")
            self.logger.debug("Exception details:", exc_info=exception)
        else:
            self.logger.error(message)
        
        self.session_stats['errors'] += 1
        self._update_stats('error', **kwargs)
        
    def critical(self, message, **kwargs):
        """Log critical message"""
        self.logger.critical(message)
        self.session_stats['errors'] += 1
        
    def source_started(self, source_name, url):
        """Log source scraping start"""
        self.logger.info(f"Scraping {source_name}...")
        self.logger.debug(f"   🔗 Fetching feed: {url}")
        
    def source_completed(self, source_name, article_count, cache_stats=None):
        """Log source scraping completion"""
        self.logger.info(f"   └─ Found {article_count} articles")
        if cache_stats:
            self.logger.info(f"   └─ Cached: {cache_stats['new_cached']} new, {cache_stats['updated']} updated")
        
        self.session_stats['sources_processed'] += 1
        self.session_stats['articles_processed'] += article_count
        
    def source_failed(self, source_name, error):
        """Log source scraping failure"""
        self.logger.error(f"   └─ ❌ Error scraping {source_name}: {error}")
        
    def processing_summary(self, total_articles, filtered_articles, avg_relevance):
        """Log processing summary"""
        self.logger.info(f"\n📊 Processing {total_articles} total articles...")
        self.logger.info(f"   └─ {filtered_articles} articles match European criteria")
        self.logger.info(f"   📊 Enhanced relevance stats:")
        self.logger.info(f"      • Average relevance: {avg_relevance:.1f}⭐")
        
    def category_stats(self, category_stats):
        """Log category breakdown"""
        for category, count in category_stats.items():
            self.logger.info(f"      • {category.replace('_', ' ').title()}: {count}")
            
    def cache_operations(self, operation, details):
        """Log cache operations"""
        if operation == 'cleanup':
            self.logger.info(f"   🧹 Cleaned {details['removed']} old articles from cache")
        elif operation == 'deduplication':
            self.logger.info(f"   ✅ Removed {details['removed']} duplicates, kept {details['kept']} unique articles")
            
    def report_generated(self, output_path, article_count):
        """Log report generation"""
        self.logger.info(f"📝 Generating enhanced daily report...")
        self.logger.info(f"   ✅ Report saved: {output_path}")
        self.logger.info(f"   📄 Contains {article_count} European tech articles")
        
    def github_action_summary(self):
        """Generate GitHub Actions job summary"""
        if os.getenv('GITHUB_ACTION', 'false').lower() != 'true':
            return
            
        try:
            summary_file = os.getenv('GITHUB_STEP_SUMMARY')
            if not summary_file:
                return
                
            duration = datetime.now() - self.session_stats['start_time']
            
            summary_content = f"""
## 📊 Europa Tech Tracker Execution Summary

**Duration:** {duration.total_seconds():.1f} seconds  
**Sources processed:** {self.session_stats['sources_processed']}  
**Articles processed:** {self.session_stats['articles_processed']}  
**Warnings:** {self.session_stats['warnings']}  
**Errors:** {self.session_stats['errors']}  

**Log file:** `{self.log_file.name}`
"""
            
            with open(summary_file, 'a', encoding='utf-8') as f:
                f.write(summary_content)
                
        except Exception as e:
            self.logger.warning(f"Could not write GitHub Actions summary: {e}")
            
    def save_session_stats(self):
        """Save session statistics to JSON file"""
        try:
            stats_file = self.log_dir / f"session_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Calculate final stats
            self.session_stats['end_time'] = datetime.now()
            self.session_stats['duration_seconds'] = (
                self.session_stats['end_time'] - self.session_stats['start_time']
            ).total_seconds()
            
            # Convert datetime objects to ISO format for JSON serialization
            json_stats = self.session_stats.copy()
            for key, value in json_stats.items():
                if isinstance(value, datetime):
                    json_stats[key] = value.isoformat()
            
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(json_stats, f, indent=2)
                
            self.logger.debug(f"Session stats saved to {stats_file}")
            
        except Exception as e:
            self.logger.warning(f"Could not save session stats: {e}")
    
    def _update_stats(self, level, **kwargs):
        """Update session statistics with additional context"""
        # Update custom counters based on kwargs
        for key, value in kwargs.items():
            if key in self.session_stats and isinstance(value, int):
                self.session_stats[key] += value
    
    def close(self):
        """Close logger and save final stats"""
        self.save_session_stats()
        self.github_action_summary()
        
        # Close all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Global logger instance
_logger_instance = None

def get_logger(name="europa_tech"):
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = EuropaLogger(name)
    return _logger_instance

def close_logger():
    """Close global logger"""
    global _logger_instance
    if _logger_instance:
        _logger_instance.close()
        _logger_instance = None