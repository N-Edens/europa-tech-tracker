#!/usr/bin/env python3
"""
Europa Tech Tracker - Phase 1 MVP
Main entry point for RSS scraping and processing
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from rss_scraper import RSScraper
from content_filter import ContentFilter
from markdown_output import MarkdownOutput


def load_config(config_path="config/sources.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing configuration: {e}")
        sys.exit(1)


def main():
    """Main execution function"""
    print("🇪🇺 Europa Tech Tracker - Phase 1 MVP")
    print("=" * 45)
    
    # Load configuration
    print("📁 Loading configuration...")
    config = load_config()
    
    # Initialize components
    scraper = RSScraper()
    content_filter = ContentFilter(config['keywords'])
    output_handler = MarkdownOutput()
    
    # Get enabled sources
    enabled_sources = {
        name: source for name, source in config['sources'].items() 
        if source.get('enabled', True)
    }
    
    print(f"📡 Found {len(enabled_sources)} enabled RSS sources")
    
    # Collect articles
    all_articles = []
    for source_name, source_config in enabled_sources.items():
        print(f"🔍 Scraping {source_config['name']}...")
        
        try:
            articles = scraper.fetch_articles(
                source_config['url'], 
                source_name
            )
            print(f"   └─ Found {len(articles)} articles")
            all_articles.extend(articles)
            
        except Exception as e:
            print(f"   └─ ❌ Error scraping {source_name}: {e}")
            continue
    
    print(f"\n📊 Total articles collected: {len(all_articles)}")
    
    # Filter content  
    print("🔍 Filtering for European relevance...")
    filtered_articles = content_filter.filter_articles(all_articles)
    print(f"   └─ {len(filtered_articles)} articles match European keywords")
    
    # Generate output
    if filtered_articles:
        print("📝 Generating daily report...")
        output_filename = datetime.now().strftime("europa_tech_%Y%m%d.md")
        output_path = f"output/daily_reports/{output_filename}"
        
        output_handler.generate_report(filtered_articles, output_path)
        print(f"   └─ Report saved: {output_path}")
        
        # Display summary
        categories = {}
        for article in filtered_articles:
            cat = article.get('category', 'Uncategorized')
            categories[cat] = categories.get(cat, 0) + 1
            
        print(f"\n📈 Article breakdown by relevance:")
        for category, count in categories.items():
            print(f"   • {category}: {count}")
            
    else:
        print("❌ No relevant articles found")
    
    print("\n✅ Europa Tech Tracker completed!")


if __name__ == "__main__":
    main()