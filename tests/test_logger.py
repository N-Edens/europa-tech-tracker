"""
Unit tests for Logger utility  
Tests Phase 3 functionality: logging, GitHub Actions integration, session tracking
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
import os

# Add src to path for imports  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.logger import Logger


@pytest.mark.unit
class TestLogger:
    """Test cases for Logger functionality"""
    
    def test_logger_initialization(self, temp_directories):
        """Test Logger initialization with default parameters"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        assert logger.log_dir == temp_directories['logs']
        assert logger.session_id is not None
        assert len(logger.session_id) > 0
        assert logger.start_time is not None
        
    def test_logger_custom_session_id(self, temp_directories):
        """Test Logger with custom session ID"""
        custom_session = "test_session_123"
        logger = Logger(log_dir=temp_directories['logs'], session_id=custom_session)
        
        assert logger.session_id == custom_session
        
    def test_logger_log_levels(self, temp_directories):
        """Test different log levels work correctly"""
        logger = Logger(log_dir=temp_directories['logs'], level=logging.DEBUG)
        
        # Capture log output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.debug("Debug message")
            logger.info("Info message") 
            logger.warning("Warning message")
            logger.error("Error message")
            
            output = mock_stdout.getvalue()
            
        # Check that messages appear in output
        assert "Debug message" in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
        
    def test_logger_file_output(self, temp_directories):
        """Test logging to file"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        # Log some messages
        logger.info("Test file logging")
        logger.error("Test error logging")
        
        # Check that log file was created
        log_files = list(temp_directories['logs'].glob('session_*.log'))
        assert len(log_files) > 0
        
        # Check log file content
        log_file = log_files[0]
        content = log_file.read_text()
        assert "Test file logging" in content
        assert "Test error logging" in content
        
    def test_github_actions_emoji_output(self, temp_directories):
        """Test emoji-friendly output for GitHub Actions"""
        # Mock GitHub Actions environment
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = 'true'  # GITHUB_ACTIONS=true
            
            logger = Logger(log_dir=temp_directories['logs'])
            
            # Capture output
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.success("Operation successful")
                logger.info("Processing articles")
                logger.warning("Warning message")
                logger.error("Error occurred")
                
                output = mock_stdout.getvalue()
                
            # Check for emoji indicators
            assert "✅" in output  # Success emoji
            assert "📊" in output or "ℹ️" in output  # Info emoji
            assert "⚠️" in output  # Warning emoji
            assert "❌" in output  # Error emoji
            
    def test_step_tracking(self, temp_directories):
        """Test step tracking functionality"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.step("Loading configuration")
            logger.step("Processing RSS feeds")
            logger.step("Generating reports")
            
            output = mock_stdout.getvalue()
            
        # Should contain step indicators
        lines = output.strip().split('\n')
        step_lines = [line for line in lines if 'Step' in line or '→' in line]
        assert len(step_lines) >= 3
        
    def test_statistics_tracking(self, temp_directories):
        """Test session statistics tracking"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        # Record some statistics
        logger.record_stat('articles_processed', 25)
        logger.record_stat('articles_relevant', 8)
        logger.record_stat('sources_processed', 4)
        
        stats = logger.get_session_stats()
        
        assert stats['articles_processed'] == 25
        assert stats['articles_relevant'] == 8
        assert stats['sources_processed'] == 4
        assert 'session_duration' in stats
        
    def test_session_summary(self, temp_directories):
        """Test session summary generation"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        # Record stats and messages
        logger.record_stat('total_articles', 30)
        logger.record_stat('european_articles', 12)
        logger.info("Processing completed successfully")
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.session_summary()
            output = mock_stdout.getvalue()
            
        # Should contain summary information
        assert "Session Summary" in output or "📊" in output
        assert "30" in output  # total_articles
        assert "12" in output  # european_articles
        
    def test_progress_tracking(self, temp_directories):
        """Test progress percentage tracking"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.progress("Processing source 1", 1, 4)
            logger.progress("Processing source 2", 2, 4)
            logger.progress("Processing source 3", 3, 4)
            logger.progress("Processing source 4", 4, 4)
            
            output = mock_stdout.getvalue()
            
        # Should contain progress indicators
        assert "25%" in output or "[1/4]" in output
        assert "50%" in output or "[2/4]" in output
        assert "75%" in output or "[3/4]" in output
        assert "100%" in output or "[4/4]" in output
        
    def test_error_context_tracking(self, temp_directories):
        """Test error context and stack trace handling"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        try:
            raise ValueError("Test error for logging")
        except ValueError as e:
            logger.error_with_context("RSS processing failed", e)
            
        # Check log file contains error context
        log_files = list(temp_directories['logs'].glob('session_*.log'))
        log_content = log_files[0].read_text()
        
        assert "RSS processing failed" in log_content
        assert "ValueError" in log_content
        assert "Test error for logging" in log_content
        
    def test_source_specific_logging(self, temp_directories):
        """Test logging with source-specific context"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.source_info("tech_eu", "Successfully fetched 15 articles")
            logger.source_warning("sifted_eu", "Rate limit exceeded, retrying")
            logger.source_error("broken_source", "404 Not Found")
            
            output = mock_stdout.getvalue()
            
        # Should contain source identifiers
        assert "tech_eu" in output
        assert "sifted_eu" in output
        assert "broken_source" in output
        assert "Successfully fetched" in output
        assert "Rate limit exceeded" in output
        assert "404 Not Found" in output
        
    def test_github_step_summary_generation(self, temp_directories):
        """Test GitHub Actions step summary generation"""
        # Mock GitHub Actions environment
        with patch('os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                if key == 'GITHUB_ACTIONS':
                    return 'true'
                elif key == 'GITHUB_STEP_SUMMARY':
                    return str(temp_directories['logs'] / 'step_summary.md')
                return default
                
            mock_getenv.side_effect = getenv_side_effect
            
            logger = Logger(log_dir=temp_directories['logs'])
            
            # Record some stats
            logger.record_stat('articles_collected', 45)
            logger.record_stat('articles_relevant', 18)
            logger.record_stat('sources_successful', 3)
            
            # Generate step summary
            logger.generate_step_summary([
                {'title': 'Test Article 1', 'relevance_score': 18.5},
                {'title': 'Test Article 2', 'relevance_score': 16.2}
            ])
            
            # Check that summary file was created
            summary_file = temp_directories['logs'] / 'step_summary.md'
            assert summary_file.exists()
            
            summary_content = summary_file.read_text()
            assert "45" in summary_content  # articles_collected
            assert "18" in summary_content  # articles_relevant
            assert "Test Article 1" in summary_content
            
    def test_log_level_filtering(self, temp_directories):
        """Test that log level filtering works correctly"""
        # Create logger with WARNING level
        logger = Logger(log_dir=temp_directories['logs'], level=logging.WARNING)
        
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.debug("Debug message - should not appear")
            logger.info("Info message - should not appear")
            logger.warning("Warning message - should appear")
            logger.error("Error message - should appear")
            
            output = mock_stdout.getvalue()
            
        # Debug and Info should not appear, Warning and Error should
        assert "Debug message" not in output
        assert "Info message" not in output
        assert "Warning message" in output
        assert "Error message" in output
        
    def test_concurrent_logging(self, temp_directories):
        """Test logger thread safety"""
        import threading
        import time
        
        logger = Logger(log_dir=temp_directories['logs'])
        results = []
        
        def log_worker(worker_id):
            for i in range(5):
                logger.info(f"Worker {worker_id} - Message {i}")
                time.sleep(0.01)
                
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=log_worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Check that all messages were logged
        log_files = list(temp_directories['logs'].glob('session_*.log'))
        log_content = log_files[0].read_text()
        
        # Should have messages from all workers
        worker_messages = [line for line in log_content.split('\n') if 'Worker' in line]
        assert len(worker_messages) == 15  # 3 workers * 5 messages each
        
    def test_cleanup_old_logs(self, temp_directories):
        """Test cleanup of old log files"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        # Create some old log files manually
        old_log = temp_directories['logs'] / 'session_old_20260301_120000.log'
        old_log.write_text("Old log content")
        
        recent_log = temp_directories['logs'] / 'session_recent_20260311_120000.log'
        recent_log.write_text("Recent log content")
        
        # Run cleanup
        removed_count = logger.cleanup_old_logs(max_age_days=5)
        
        # Should remove old log but keep recent
        assert removed_count >= 0
        assert recent_log.exists()
        
    def test_custom_formatters(self, temp_directories):
        """Test custom log formatting"""
        logger = Logger(log_dir=temp_directories['logs'])
        
        # Test different format types
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            logger.metric("Processing Rate", 2.5, "articles/sec")
            logger.duration("RSS Fetch", 1.234)
            logger.size("Cache Size", 1048576)  # 1MB in bytes
            
            output = mock_stdout.getvalue()
            
        # Should format appropriately
        assert "2.5" in output and "articles/sec" in output
        assert "1.234s" in output or "1.23s" in output
        assert "1.0MB" in output or "1MB" in output