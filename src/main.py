#!/usr/bin/env python3
"""
Europa Tech Tracker - Phase 2 Enhanced Processing
Main entry point for RSS scraping with deduplication, caching and multi-source support
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from rss_scraper import RSScraper
from content_filter import ContentFilter
from markdown_output import MarkdownOutput
from utils import CacheManager, ArticleDeduplicator, ConfigurationLoader


def load_configuration():
    """Load and validate configuration using enhanced config loader"""
    try:
        config_loader = ConfigurationLoader()
        config = config_loader.load_sources_config()
        return config_loader, config
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)


def initialize_components(config, config_loader):
    """Initialize all processing components"""
    print("🔧 Initializing components...")
    
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
    
    print("   ✅ All components initialized")
    
    return {
        'scraper': scraper,
        'content_filter': content_filter,
        'output_handler': output_handler,
        'cache_manager': cache_manager, 
        'deduplicator': deduplicator
    }


def collect_articles(components, enabled_sources):
    """Collect articles from all enabled sources"""
    scraper = components['scraper']
    cache_manager = components['cache_manager']
    
    all_articles = []
    source_stats = {}
    
    for source_name, source_config in enabled_sources.items():
        print(f"🔍 Scraping {source_config['name']}...")
        
        try:
            # Fetch articles
            articles = scraper.fetch_articles(
                source_config['url'],
                source_name
            )
            
            if articles:
                # Cache articles
                cache_stats = cache_manager.cache_articles(articles, source_name)
                
                print(f"   └─ Found {len(articles)} articles")
                print(f"   └─ Cached: {cache_stats['new_cached']} new, {cache_stats['updated']} updated")
                
                all_articles.extend(articles)
                source_stats[source_name] = {
                    'articles': len(articles),
                    'cache_stats': cache_stats
                }
            
        except Exception as e:
            print(f"   └─ ❌ Error scraping {source_name}: {e}")
            source_stats[source_name] = {'error': str(e)}
            continue
    
    return all_articles, source_stats


def process_articles(components, articles):
    """Process articles through filtering and deduplication"""
    content_filter = components['content_filter']
    deduplicator = components['deduplicator']
    
    print(f"\n📊 Processing {len(articles)} total articles...")
    
    # Step 1: Remove duplicates
    unique_articles = deduplicator.remove_duplicates(articles)
    
    # Step 2: Filter for European relevance  
    print("🔍 Filtering for European relevance...")
    filtered_articles = content_filter.filter_articles(unique_articles)
    
    if filtered_articles:
        print(f"   └─ {len(filtered_articles)} articles match European criteria")
        
        # Display enhanced filtering stats
        category_stats = {}
        total_relevance = 0
        
        for article in filtered_articles:
            category = article.get('primary_category', 'general')
            category_stats[category] = category_stats.get(category, 0) + 1
            total_relevance += article.get('relevance_score', 0)
        
        avg_relevance = total_relevance / len(filtered_articles) if filtered_articles else 0
        
        print(f"   📊 Enhanced relevance stats:")
        for category, count in category_stats.items():
            print(f"      • {category.replace('_', ' ').title()}: {count}")
        print(f"      • Average relevance: {avg_relevance:.1f}⭐")
        
    else:
        print("   ❌ No articles meet European relevance criteria")
    
    return filtered_articles


def generate_output(components, articles, config_loader, config):
    """Generate and save reports"""
    output_handler = components['output_handler']
    output_settings = config_loader.get_output_settings(config)
    
    if not articles:
        print("❌ No articles to generate report for")
        return None
    
    print("📝 Generating enhanced daily report...")
    
    # Generate output filename with timestamp
    timestamp = datetime.now()
    output_filename = timestamp.strftime("europa_tech_%Y%m%d_%H%M.md")
    output_path = f"output/daily_reports/{output_filename}"
    
    # Add enhanced metadata to articles
    report_metadata = {
        'generated_at': timestamp.isoformat(),
        'total_sources': len(config.get('sources', {})),
        'enabled_sources': len([s for s in config.get('sources', {}).values() if s.get('enabled', True)]),
        'processing_version': '2.0',
        'features': ['deduplication', 'caching', 'enhanced_filtering']
    }
    
    # Generate report
    output_handler.generate_report(articles, output_path)
    
    # Also generate quick summary for console
    summary = output_handler.create_quick_summary(articles, max_articles=5)
    print(f"\n📋 Quick Summary:")
    print(summary)
    
    return output_path


def display_session_stats(components, source_stats):
    """Display comprehensive session statistics"""
    cache_manager = components['cache_manager']
    deduplicator = components['deduplicator']
    
    print(f"\n📈 Session Statistics:")
    print(f"   🌐 Source Performance:")
    
    for source_name, stats in source_stats.items():
        if 'error' in stats:
            print(f"      ❌ {source_name}: {stats['error']}")
        else:
            articles = stats['articles']
            cache_stats = stats['cache_stats']
            print(f"      ✅ {source_name}: {articles} articles, {cache_stats['new_cached']} new cached")
    
    # Cache statistics
    cache_stats = cache_manager.get_cache_stats()
    print(f"   💾 Cache Status:")
    print(f"      • Total cached articles: {cache_stats['total_articles']}")
    print(f"      • Cache size: {cache_stats['cache_size_mb']} MB")
    
    # Deduplication statistics
    dedup_stats = deduplicator.get_cache_stats()
    print(f"   🔍 Deduplication Cache:")
    print(f"      • Tracked URLs: {dedup_stats['total_urls']}")
    print(f"      • Similarity threshold: {dedup_stats['similarity_threshold']}")


def main():
    """Main execution function for Phase 2"""
    print("🇪🇺 Europa Tech Tracker - Phase 2 Enhanced")
    print("=" * 50)
    
    # Load enhanced configuration
    print("📁 Loading enhanced configuration...")
    config_loader, config = load_configuration()
    
    # Initialize all components
    components = initialize_components(config, config_loader)
    
    # Get enabled sources
    enabled_sources = config_loader.get_enabled_sources(config)
    
    if not enabled_sources:
        print("❌ No enabled sources found!")
        sys.exit(1)
    
    # Collect articles from all sources
    all_articles, source_stats = collect_articles(components, enabled_sources)
    
    if not all_articles:
        print("❌ No articles collected from any source!")
        return
    
    # Process articles (deduplication + filtering)
    filtered_articles = process_articles(components, all_articles)
    
    # Generate output
    output_path = generate_output(components, filtered_articles, config_loader, config)
    
    # Display comprehensive statistics
    display_session_stats(components, source_stats)
    
    # Cleanup old cache entries
    components['cache_manager'].cleanup_old_articles(max_age_days=30)
    components['deduplicator']._clean_old_entries(max_age_days=7)
    
    if output_path:
        print(f"\n✅ Europa Tech Tracker Phase 2 completed successfully!")
        print(f"📄 Report saved: {output_path}")
    else:
        print(f"\n⚠️  Europa Tech Tracker completed with no output")


if __name__ == "__main__":
    main()