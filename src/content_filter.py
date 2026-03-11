"""
Content Filter Module for Europa Tech Tracker  
Filters articles based on European relevance keywords and categories
"""

import re
from typing import List, Dict, Any
from collections import defaultdict


class ContentFilter:
    """Filters articles based on keyword matching and relevance scoring"""
    
    def __init__(self, keyword_config):
        """
        Initialize content filter with keyword configuration
        
        Args:
            keyword_config (dict): Keywords organized by category
        """
        self.keywords = keyword_config
        self.keyword_patterns = self._compile_keyword_patterns()
        self.min_relevance_score = 1  # Minimum keywords to match
        
    def _compile_keyword_patterns(self):
        """Compile regex patterns for efficient keyword matching"""
        patterns = {}
        
        for category, keyword_list in self.keywords.items():
            if not isinstance(keyword_list, list):
                continue
                
            # Create case-insensitive regex patterns
            compiled_patterns = []
            for keyword in keyword_list:
                if isinstance(keyword, str) and keyword.strip():
                    # Escape special regex characters and create word boundary pattern
                    escaped = re.escape(keyword.strip())
                    pattern = re.compile(rf'\b{escaped}\b', re.IGNORECASE)
                    compiled_patterns.append((keyword, pattern))
            
            patterns[category] = compiled_patterns
            
        return patterns
    
    def filter_articles(self, articles):
        """
        Filter articles based on European relevance keywords
        
        Args:
            articles (list): List of article dictionaries
        
        Returns:
            list: Filtered articles with relevance scores
        """
        print(f"   🔍 Analyzing {len(articles)} articles...")
        
        filtered_articles = []
        category_stats = defaultdict(int)
        
        for article in articles:
            relevance_result = self._calculate_relevance(article)
            
            if relevance_result['total_score'] >= self.min_relevance_score:
                # Add relevance metadata to article
                article['relevance_score'] = relevance_result['total_score']
                article['matched_keywords'] = relevance_result['matched_keywords']
                article['primary_category'] = relevance_result['primary_category']
                article['category'] = relevance_result['primary_category']  # For backwards compatibility
                
                filtered_articles.append(article)
                category_stats[relevance_result['primary_category']] += 1
        
        # Print filtering stats
        print(f"   📊 Relevance stats:")
        for category, count in category_stats.items():
            print(f"      • {category.replace('_', ' ').title()}: {count}")
        
        return filtered_articles
    
    def _calculate_relevance(self, article):
        """
        Calculate relevance score for an article based on keyword matches
        
        Args:
            article (dict): Article dictionary
        
        Returns:
            dict: Relevance analysis result
        """
        # Combine all searchable text
        searchable_text = self._get_searchable_text(article)
        
        matched_keywords = defaultdict(list)
        category_scores = defaultdict(int)
        
        # Check each category's keywords
        for category, pattern_list in self.keyword_patterns.items():
            for keyword, pattern in pattern_list:
                matches = pattern.findall(searchable_text)
                if matches:
                    matched_keywords[category].append({
                        'keyword': keyword,
                        'occurrences': len(matches)
                    })
                    # Weight by number of occurrences
                    category_scores[category] += len(matches)
        
        # Determine primary category (highest scoring)
        primary_category = 'General'
        if category_scores:
            primary_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # Calculate total relevance score
        total_score = sum(category_scores.values())
        
        return {
            'total_score': total_score,
            'category_scores': dict(category_scores),
            'matched_keywords': dict(matched_keywords),
            'primary_category': primary_category
        }
    
    def _get_searchable_text(self, article):
        """
        Extract all searchable text from an article
        
        Args:
            article (dict): Article dictionary
        
        Returns:
            str: Combined searchable text
        """
        text_fields = [
            article.get('title', ''),
            article.get('description', ''),
            article.get('content', ''),
            ' '.join(article.get('tags', []))
        ]
        
        # Combine and clean text
        combined_text = ' '.join(text_fields).strip()
        
        # Normalize whitespace
        combined_text = re.sub(r'\s+', ' ', combined_text)
        
        return combined_text
    
    def get_keyword_stats(self, articles):
        """
        Get statistics about keyword matches across a set of articles
        
        Args:
            articles (list): List of articles (should be already filtered)
        
        Returns:
            dict: Keyword statistics
        """
        stats = {
            'total_articles': len(articles),
            'keyword_frequency': defaultdict(int),
            'category_distribution': defaultdict(int),
            'avg_relevance_score': 0
        }
        
        total_relevance = 0
        
        for article in articles:
            # Count relevance scores
            relevance_score = article.get('relevance_score', 0)
            total_relevance += relevance_score
            
            # Count category distribution
            category = article.get('primary_category', 'General')
            stats['category_distribution'][category] += 1
            
            # Count keyword frequency
            matched_keywords = article.get('matched_keywords', {})
            for category, keyword_list in matched_keywords.items():
                for keyword_info in keyword_list:
                    keyword = keyword_info['keyword']
                    occurrences = keyword_info['occurrences']
                    stats['keyword_frequency'][keyword] += occurrences
        
        # Calculate average relevance
        if len(articles) > 0:
            stats['avg_relevance_score'] = total_relevance / len(articles)
        
        return stats
    
    def add_custom_keywords(self, category, keywords):
        """
        Dynamically add custom keywords to a category
        
        Args:
            category (str): Category name
            keywords (list): List of keyword strings
        """
        if category not in self.keywords:
            self.keywords[category] = []
        
        # Add new keywords
        for keyword in keywords:
            if isinstance(keyword, str) and keyword.strip():
                self.keywords[category].append(keyword.strip())
        
        # Recompile patterns
        self.keyword_patterns = self._compile_keyword_patterns()
    
    def update_minimum_score(self, min_score):
        """
        Update the minimum relevance score threshold
        
        Args:
            min_score (int): New minimum score
        """
        self.min_relevance_score = max(1, int(min_score))
    
    def preview_filtering(self, articles, limit=5):
        """
        Preview filtering results without applying them
        
        Args:
            articles (list): Articles to preview
            limit (int): Maximum number of results to show
        
        Returns:
            dict: Preview results
        """
        preview_results = []
        
        for article in articles[:limit]:
            relevance_result = self._calculate_relevance(article)
            
            preview_results.append({
                'title': article.get('title', 'No title'),
                'url': article.get('url', ''),
                'relevance_score': relevance_result['total_score'],
                'matched_keywords': relevance_result['matched_keywords'],
                'primary_category': relevance_result['primary_category'],
                'would_pass': relevance_result['total_score'] >= self.min_relevance_score
            })
        
        return {
            'preview_count': len(preview_results),
            'results': preview_results,
            'total_would_pass': sum(1 for r in preview_results if r['would_pass'])
        }