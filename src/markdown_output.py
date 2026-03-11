"""
Markdown Output Module for Europa Tech Tracker
Generates formatted markdown reports from filtered articles
"""

import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import textwrap


class MarkdownOutput:
    """Generates structured markdown reports from article data"""
    
    def __init__(self):
        self.report_template = {
            'header': True,
            'summary': True,
            'category_breakdown': True,
            'articles': True,
            'footer': True
        }
    
    def generate_report(self, articles, output_path, title=None):
        """
        Generate a complete markdown report from filtered articles
        
        Args:
            articles (list): List of filtered article dictionaries
            output_path (str): Path to save the report
            title (str): Custom title for the report  
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Generate report content
        report_content = self._build_report_content(articles, title)
        
        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"   ✅ Report saved: {output_path}")
        except IOError as e:
            print(f"   ❌ Error saving report: {e}")
    
    def _build_report_content(self, articles, title=None):
        """Build the complete markdown report content"""
        content_parts = []
        
        # Header
        if self.report_template['header']:
            content_parts.append(self._generate_header(articles, title))
        
        # Summary
        if self.report_template['summary']:
            content_parts.append(self._generate_summary(articles))
        
        # Category breakdown
        if self.report_template['category_breakdown']:
            content_parts.append(self._generate_category_breakdown(articles))
        
        # Articles
        if self.report_template['articles']:
            content_parts.append(self._generate_articles_section(articles))
        
        # Footer
        if self.report_template['footer']:
            content_parts.append(self._generate_footer())
        
        return '\n\n'.join(content_parts)
    
    def _generate_header(self, articles, title=None):
        """Generate report header with metadata"""
        today = datetime.now()
        
        if title is None:
            title = f"Europa Tech News - {today.strftime('%B %d, %Y')}"
        
        header = f"""# 🇪🇺 {title}

**Automated daily tracker for European technology news**

---

📅 **Generated:** {today.strftime('%B %d, %Y at %H:%M')}  
📊 **Articles found:** {len(articles)}  
🔍 **Sources:** {self._count_sources(articles)}  
⭐ **Avg. relevance:** {self._calculate_avg_relevance(articles):.1f}  """

        return header
    
    def _generate_summary(self, articles):
        """Generate executive summary section"""
        if not articles:
            return "## 📋 Summary\n\nNo relevant European tech articles found today."
        
        # Get top categories
        categories = self._get_category_stats(articles)
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Get top keywords
        all_keywords = []
        for article in articles:
            matched_keywords = article.get('matched_keywords', {})
            for cat_keywords in matched_keywords.values():
                for kw_info in cat_keywords:
                    all_keywords.extend([kw_info['keyword']] * kw_info['occurrences'])
        
        keyword_freq = defaultdict(int)
        for kw in all_keywords:
            keyword_freq[kw] += 1
        
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        summary = f"""## 📋 Executive Summary

Today's European tech news highlights:

### 🔥 Top Categories
{chr(10).join([f"• **{cat.replace('_', ' ').title()}**: {count} articles" for cat, count in top_categories])}

### 🏷️ Trending Keywords
{', '.join([f"*{kw}* ({count})" for kw, count in top_keywords])}

### 📈 Key Insights
• **Most active category:** {top_categories[0][0].replace('_', ' ').title() if top_categories else 'N/A'}
• **European focus areas:** {', '.join([cat.replace('_', ' ').title() for cat, _ in top_categories])}
• **Article quality:** {len([a for a in articles if a.get('relevance_score', 0) >= 3])} high-relevance articles"""

        return summary
    
    def _generate_category_breakdown(self, articles):
        """Generate breakdown by category"""
        categories = self._get_category_stats(articles)
        
        if not categories:
            return ""
        
        breakdown = "## 🗂️ Category Breakdown\n\n"
        
        # Sort categories by count
        sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            percentage = (count / len(articles)) * 100
            
            # Get category emoji
            emoji = self._get_category_emoji(category)
            
            breakdown += f"### {emoji} {category.replace('_', ' ').title()}\n"
            breakdown += f"**{count} articles** ({percentage:.0f}% of total)\n\n"
            
            # List articles in this category
            category_articles = [a for a in articles if a.get('primary_category') == category]
            category_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            for article in category_articles[:3]:  # Show top 3
                title = article.get('title', 'Untitled')[:60]
                if len(article.get('title', '')) > 60:
                    title += "..."
                relevance = article.get('relevance_score', 0)
                
                breakdown += f"• [{title}]({article.get('url', '#')}) `[{relevance}⭐]`\n"
            
            if len(category_articles) > 3:
                breakdown += f"• *...and {len(category_articles) - 3} more articles*\n"
            
            breakdown += "\n"
        
        return breakdown.rstrip()
    
    def _generate_articles_section(self, articles):
        """Generate detailed articles section"""
        if not articles:
            return ""
        
        # Group articles by category
        categorized_articles = defaultdict(list)
        for article in articles:
            category = article.get('primary_category', 'general')
            categorized_articles[category].append(article)
        
        articles_content = "## 📰 Detailed Articles\n\n"
        
        for category in sorted(categorized_articles.keys()):
            category_articles = categorized_articles[category]
            
            # Sort by relevance score
            category_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            emoji = self._get_category_emoji(category)
            articles_content += f"### {emoji} {category.replace('_', ' ').title()}\n\n"
            
            for i, article in enumerate(category_articles, 1):
                articles_content += self._format_article(article, i)
                articles_content += "\n---\n\n"
        
        return articles_content.rstrip()
    
    def _format_article(self, article, index):
        """Format individual article for markdown"""
        title = article.get('title', 'Untitled Article')
        url = article.get('url', '#')
        description = article.get('description', '')
        source = article.get('source', 'Unknown')
        published = article.get('published', '')
        relevance_score = article.get('relevance_score', 0)
        matched_keywords = article.get('matched_keywords', {})
        
        # Format publication date
        try:
            if published:
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                formatted_date = pub_date.strftime('%B %d, %Y')
            else:
                formatted_date = 'Unknown date'
        except:
            formatted_date = 'Unknown date'
        
        # Format matched keywords
        all_keywords = []
        for cat_keywords in matched_keywords.values():
            for kw_info in cat_keywords:
                all_keywords.append(kw_info['keyword'])
        keywords_str = ', '.join(f"`{kw}`" for kw in sorted(set(all_keywords))[:5])
        
        article_md = f"""#### {index}. [{title}]({url})

**Source:** {source.replace('_', ' ').title()} | **Published:** {formatted_date} | **Relevance:** {relevance_score}⭐

{self._wrap_text(description, 80) if description else '*No description available*'}

**Keywords:** {keywords_str if keywords_str else '*None*'}"""
        
        return article_md
    
    def _generate_footer(self):
        """Generate report footer"""
        footer = f"""---

## 🔧 About This Report

This automated report was generated by **Europa Tech Tracker**, a tool for tracking European technology news and alternatives to American tech solutions.

**Features:**
- 📡 RSS feed monitoring from European tech sources
- 🔍 Keyword-based filtering for European relevance  
- 🗂️ Automatic categorization by topic
- ⭐ Relevance scoring for content quality

**Generated at:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

*🇪🇺 Supporting European digital sovereignty, one news article at a time.*"""

        return footer
    
    def _count_sources(self, articles):
        """Count unique sources in articles"""
        sources = set(article.get('source', 'Unknown') for article in articles)
        return len(sources)
    
    def _calculate_avg_relevance(self, articles):
        """Calculate average relevance score"""
        if not articles:
            return 0.0
        
        total_relevance = sum(article.get('relevance_score', 0) for article in articles)
        return total_relevance / len(articles)
    
    def _get_category_stats(self, articles):
        """Get article count by category"""
        categories = defaultdict(int)
        for article in articles:
            category = article.get('primary_category', 'general')
            categories[category] += 1
        return dict(categories)
    
    def _get_category_emoji(self, category):
        """Get appropriate emoji for category"""
        emoji_map = {
            'european_companies': '🏢',
            'privacy_tech': '🔒',
            'companies': '🏭',
            'policy': '🏛️',
            'general': '📰',
            'startup': '🚀',
            'cloud': '☁️',
            'opensource': '💻',
            'ai': '🤖',
            'security': '🛡️',
            'fintech': '💰',
            'mobility': '🚗'
        }
        
        return emoji_map.get(category.lower(), '📰')
    
    def _wrap_text(self, text, width=80):
        """Wrap text to specified width"""
        if not text:
            return ""
        
        return textwrap.fill(text, width=width, subsequent_indent='')
    
    def create_quick_summary(self, articles, max_articles=10):
        """
        Create a quick text summary for terminal output
        
        Args:
            articles (list): Filtered articles
            max_articles (int): Maximum articles to include
        
        Returns:
            str: Quick summary text
        """
        if not articles:
            return "No relevant European tech articles found."
        
        summary_lines = []
        summary_lines.append(f"🇪🇺 Found {len(articles)} European tech articles")
        summary_lines.append("")
        
        # Top categories
        categories = self._get_category_stats(articles)
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for category, count in top_categories:
            emoji = self._get_category_emoji(category)
            summary_lines.append(f"{emoji} {category.replace('_', ' ').title()}: {count}")
        
        summary_lines.append("")
        summary_lines.append(f"📝 Top {min(max_articles, len(articles))} articles:")
        
        # Sort by relevance and show top articles
        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        for i, article in enumerate(sorted_articles[:max_articles], 1):
            title = article.get('title', 'Untitled')
            if len(title) > 60:
                title = title[:57] + "..."
            
            source = article.get('source', 'Unknown').replace('_', ' ').title()
            relevance = article.get('relevance_score', 0)
            
            summary_lines.append(f"{i:2d}. {title} [{source}] ({relevance}⭐)")
        
        return '\n'.join(summary_lines)
    
    def create_google_docs_content(self, articles):
        """
        Create formatted content suitable for Google Docs upload
        
        Args:
            articles (list): Filtered articles
            
        Returns:
            str: Formatted content for Google Docs
        """
        if not articles:
            return "No relevant European tech articles found today."
        
        # Build Google Docs optimized content
        content_parts = []
        
        # Title and date
        today = datetime.now()
        content_parts.append(f"🇪🇺 Europa Tech Daily Report - {today.strftime('%B %d, %Y')}")
        content_parts.append("")
        
        # Quick statistics
        categories = self._get_category_stats(articles)
        avg_relevance = self._calculate_avg_relevance(articles)
        
        content_parts.append("📊 Daily Summary:")
        content_parts.append(f"• Total European tech articles: {len(articles)}")
        content_parts.append(f"• Average relevance score: {avg_relevance:.1f}⭐")
        content_parts.append(f"• Active sources: {self._count_sources(articles)}")
        
        # Top categories
        if categories:
            top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:3]
            cat_strs = [f"{cat.replace('_', ' ').title()} ({count})" for cat, count in top_categories]
            content_parts.append(f"• Top categories: {', '.join(cat_strs)}")
        
        content_parts.append("")
        content_parts.append("🗞️ Top European Tech Articles:")
        content_parts.append("")
        
        # Sort articles by relevance and list top ones
        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        for i, article in enumerate(sorted_articles[:15], 1):  # Top 15 articles
            title = article.get('title', 'Untitled')
            url = article.get('url', '')
            source = article.get('source', 'Unknown').replace('_', ' ').title()
            relevance = article.get('relevance_score', 0)
            category = article.get('primary_category', 'general').replace('_', ' ').title()
            
            # Format article entry for Google Docs
            content_parts.append(f"{i}. {title}")
            if url:
                content_parts.append(f"   🔗 {url}")
            content_parts.append(f"   📊 {relevance:.1f}⭐ | 📰 {source} | 🏷️ {category}")
            content_parts.append("")
        
        # Add timestamp
        content_parts.append("---")
        content_parts.append(f"Generated: {today.strftime('%Y-%m-%d %H:%M UTC')}")
        
        return '\n'.join(content_parts)