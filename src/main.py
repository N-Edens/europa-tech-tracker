#!/usr/bin/env python3
"""
Europa Tech Tracker - Phase 3 Automation
Main entry point with GitHub Actions integration and enhanced logging
"""

import os
import sys
import atexit
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from rss_scraper import RSScraper
from content_filter import ContentFilter
from markdown_output import MarkdownOutput
from utils import CacheManager, ArticleDeduplicator, ConfigurationLoader, get_logger, close_logger

# Initialize logger
logger = get_logger("europa_tech_main")

# Ensure logger is closed on exit
atexit.register(close_logger)


def load_configuration():
    """Load and validate configuration using enhanced config loader"""
    try:
        logger.info("Loading enhanced configuration...")
        config_loader = ConfigurationLoader()
        config = config_loader.load_sources_config()
        logger.debug("Configuration loaded successfully")
        return config_loader, config
    except Exception as e:
        logger.critical(f"Error loading configuration: {e}", exception=e)
        sys.exit(1)


def initialize_components(config, config_loader):
    """Initialize all processing components"""
    logger.info("Initializing components...")
    
    try:
        # RSS Scraper
        scraper = RSScraper()
        
        # Content Filter with enhanced keywords
        keywords = config_loader.get_keywords_by_category(config)
        content_filter = ContentFilter(keywords)
        
        # Output Handler
        output_handler = MarkdownOutput()
        
        # Cache Manager 
        cache_manager = CacheManager()
        
        # Deduplicator
        deduplicator = ArticleDeduplicator()
        
        logger.info("All components initialized successfully")
        
        return {
            'scraper': scraper,
            'content_filter': content_filter,
            'output_handler': output_handler,
            'cache_manager': cache_manager, 
            'deduplicator': deduplicator
        }
        
    except Exception as e:
        logger.critical(f"Error initializing components: {e}", exception=e)
        sys.exit(1)


def collect_articles(components, enabled_sources):
    """Collect articles from all enabled sources"""
    scraper = components['scraper']
    cache_manager = components['cache_manager']
    
    all_articles = []
    source_stats = {}
    successful_sources = 0
    
    logger.info(f"Starting collection from {len(enabled_sources)} enabled sources")
    
    for source_name, source_config in enabled_sources.items():
        try:
            logger.source_started(source_config['name'], source_config['url'])
            
            # Fetch articles
            articles = scraper.fetch_articles(
                source_config['url'],
                source_name
            )
            
            if articles:
                # Cache articles
                cache_stats = cache_manager.cache_articles(articles, source_name)
                logger.source_completed(source_config['name'], len(articles), cache_stats)
                
                all_articles.extend(articles)
                source_stats[source_name] = {
                    'articles': len(articles),
                    'cache_stats': cache_stats,
                    'status': 'success'
                }
                successful_sources += 1
            else:
                logger.warning(f"No articles returned from {source_config['name']}")
                source_stats[source_name] = {
                    'articles': 0,
                    'status': 'no_articles'
                }
            
        except Exception as e:
            logger.source_failed(source_config['name'], str(e))
            source_stats[source_name] = {
                'error': str(e),
                'status': 'failed'
            }
            continue
    
    logger.info(f"Collection completed: {successful_sources}/{len(enabled_sources)} sources successful")
    return all_articles, source_stats


def process_articles(components, articles):
    """Process articles through filtering and deduplication"""
    content_filter = components['content_filter']
    deduplicator = components['deduplicator']
    
    if not articles:
        logger.warning("No articles to process")
        return []
    
    logger.info(f"Starting processing pipeline for {len(articles)} articles")
    
    try:
        # Step 1: Remove duplicates
        logger.debug("Starting deduplication...")
        unique_articles = deduplicator.remove_duplicates(articles)
        removed_duplicates = len(articles) - len(unique_articles)
        
        logger.cache_operations('deduplication', {
            'removed': removed_duplicates,
            'kept': len(unique_articles)
        })
        
        # Step 2: Filter for European relevance  
        logger.debug("Starting relevance filtering...")
        filtered_articles = content_filter.filter_articles(unique_articles)
        
        if filtered_articles:
            # Calculate enhanced stats
            category_stats = {}
            total_relevance = 0
            
            for article in filtered_articles:
                category = article.get('primary_category', 'general')
                category_stats[category] = category_stats.get(category, 0) + 1
                total_relevance += article.get('relevance_score', 0)
            
            avg_relevance = total_relevance / len(filtered_articles)
            
            logger.processing_summary(len(unique_articles), len(filtered_articles), avg_relevance)
            logger.category_stats(category_stats)
            
        else:
            logger.warning("No articles meet European relevance criteria")
        
        return filtered_articles
        
    except Exception as e:
        logger.error(f"Error during article processing: {e}", exception=e)
        return []


def generate_output(components, articles, config_loader, config):
    """Generate and save reports"""
    output_handler = components['output_handler']
    
    if not articles:
        logger.warning("No articles to generate report for")
        return None
    
    try:
        logger.debug("Starting report generation...")
        
        # Generate output filename with timestamp
        timestamp = datetime.now()
        output_filename = timestamp.strftime("europa_tech_%Y%m%d_%H%M.md")
        output_path = f"output/daily_reports/{output_filename}"
        
        # Generate report
        output_handler.generate_report(articles, output_path)
        logger.report_generated(output_path, len(articles))
        
        # Generate quick summary for console
        summary = output_handler.create_quick_summary(articles, max_articles=5)
        logger.info("Quick Summary:")
        for line in summary.split('\n'):
            if line.strip():
                logger.info(line)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error generating output: {e}", exception=e)
        return None


def display_session_stats(components, source_stats):
    """Display comprehensive session statistics"""
    cache_manager = components['cache_manager']
    deduplicator = components['deduplicator']
    
    try:
        logger.info("Session Statistics:")
        logger.info("Source Performance:")
        
        successful_sources = 0
        total_articles = 0
        
        for source_name, stats in source_stats.items():
            if stats.get('status') == 'failed':
                logger.info(f"   ❌ {source_name}: {stats.get('error', 'Unknown error')}")
            elif stats.get('status') == 'no_articles':
                logger.info(f"   ⚠️  {source_name}: No articles found")
            else:
                articles = stats.get('articles', 0)
                cache_stats = stats.get('cache_stats', {})
                logger.info(f"   ✅ {source_name}: {articles} articles, {cache_stats.get('new_cached', 0)} new cached")
                successful_sources += 1
                total_articles += articles
        
        # Cache statistics
        cache_stats = cache_manager.get_cache_stats()
        logger.info("Cache Status:")
        logger.info(f"   • Total cached articles: {cache_stats['total_articles']}")
        logger.info(f"   • Cache size: {cache_stats['cache_size_mb']} MB")
        
        # Deduplication statistics
        dedup_stats = deduplicator.get_cache_stats()
        logger.info("Deduplication Cache:")
        logger.info(f"   • Tracked URLs: {dedup_stats['total_urls']}")
        logger.info(f"   • Similarity threshold: {dedup_stats['similarity_threshold']}")
        
        # Overall stats
        logger.info(f"Overall Session: {successful_sources} sources successful, {total_articles} total articles")
        
    except Exception as e:
        logger.error(f"Error generating session stats: {e}", exception=e)


def perform_maintenance(components):
    """Perform routine maintenance tasks"""
    try:
        logger.debug("Performing maintenance tasks...")
        
        # Cleanup old cache entries
        cache_manager = components['cache_manager']
        deduplicator = components['deduplicator']
        
        removed_cache = cache_manager.cleanup_old_articles(max_age_days=30)
        if removed_cache > 0:
            logger.cache_operations('cleanup', {'removed': removed_cache})
        
        deduplicator._clean_old_entries(max_age_days=7)
        
        logger.debug("Maintenance completed successfully")
        
    except Exception as e:
        logger.warning(f"Maintenance tasks partially failed: {e}", exception=e)


def main():
    """Main execution function for Phase 3"""
    try:
        logger.info("🇪🇺 Europa Tech Tracker - Phase 3 Automation")
        logger.info("=" * 55)
        
        # Load enhanced configuration
        config_loader, config = load_configuration()
        
        # Initialize all components
        components = initialize_components(config, config_loader)
        
        # Get enabled sources
        enabled_sources = config_loader.get_enabled_sources(config)
        
        if not enabled_sources:
            logger.critical("No enabled sources found!")
            sys.exit(1)
        
        # Collect articles from all sources
        all_articles, source_stats = collect_articles(components, enabled_sources)
        
        if not all_articles:
            logger.warning("No articles collected from any source!")
            logger.info("This might be temporary. Cache and logs have been preserved.")
        else:
            # Process articles (deduplication + filtering)
            filtered_articles = process_articles(components, all_articles)
            
            # Generate output
            output_path = generate_output(components, filtered_articles, config_loader, config)
            
            if output_path:
                logger.info(f"✅ Europa Tech Tracker completed successfully!")
                logger.info(f"📄 Report saved: {output_path}")
            else:
                logger.warning("⚠️  Europa Tech Tracker completed with no output")
        
        # Display comprehensive statistics
        display_session_stats(components, source_stats)
        
        # Perform maintenance
        perform_maintenance(components)
        
        # Exit with appropriate code
        if not all_articles:
            sys.exit(2)  # Warning exit code
        elif not any(s.get('status') == 'success' for s in source_stats.values()):
            sys.exit(3)  # No sources successful
        else:
            sys.exit(0)  # Success
        
    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"Unexpected error in main execution: {e}", exception=e)
        sys.exit(1)
    finally:
        logger.info("Europa Tech Tracker session ended")


if __name__ == "__main__":
    main()