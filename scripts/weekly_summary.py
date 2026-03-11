#!/usr/bin/env python3
"""
Weekly Europa Tech Summary — trend analysis and report generation.
Called by the weekly_summary GitHub Actions workflow.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter


def load_cache_data():
    """Load cached articles."""
    cache_file = Path("data/cache/article_cache.json")
    if not cache_file.exists():
        return []
    with open(cache_file, 'r', encoding='utf-8') as f:
        return list(json.load(f).values())


def analyze_weekly_trends(articles, days_back=7):
    """Analyse trends over the specified period."""
    cutoff = datetime.now() - timedelta(days=days_back)

    recent = []
    for a in articles:
        try:
            ts = datetime.fromisoformat(a.get('cached_at', ''))
            if ts >= cutoff:
                recent.append(a)
        except (ValueError, TypeError):
            continue

    trends = {
        'total_articles': len(recent),
        'categories': defaultdict(int),
        'sources': defaultdict(int),
        'keywords': Counter(),
        'daily_counts': defaultdict(int),
        'avg_relevance': 0,
    }

    total_rel = 0
    for a in recent:
        trends['categories'][a.get('primary_category', 'uncategorized')] += 1
        trends['sources'][a.get('source', 'unknown')] += 1

        for cat_kws in a.get('matched_keywords', {}).values():
            for kw in cat_kws:
                trends['keywords'][kw.get('keyword', '')] += kw.get('occurrences', 1)

        try:
            d = datetime.fromisoformat(a.get('cached_at', '')).strftime('%Y-%m-%d')
            trends['daily_counts'][d] += 1
        except (ValueError, TypeError):
            pass

        total_rel += a.get('relevance_score', 0)

    if trends['total_articles'] > 0:
        trends['avg_relevance'] = total_rel / trends['total_articles']

    return trends


def generate_summary_report(trends, days_back=7):
    """Generate a Markdown weekly report."""
    today = datetime.now()
    week_start = today - timedelta(days=days_back)
    total = trends['total_articles']

    top_cat = max(trends['categories'].items(), key=lambda x: x[1])[0] if trends['categories'] else 'N/A'
    top_src = max(trends['sources'].items(), key=lambda x: x[1])[0] if trends['sources'] else 'N/A'

    lines = [
        f"# \U0001f1ea\U0001f1fa Europa Tech Weekly Summary\n",
        f"**Period:** {week_start.strftime('%B %d')} - {today.strftime('%B %d, %Y')}  ",
        f"**Generated:** {today.strftime('%Y-%m-%d %H:%M UTC')}\n",
        "---\n",
        "## \U0001f4ca Week at a Glance\n",
        f"- **Total articles processed:** {total}",
        f"- **Average relevance score:** {trends['avg_relevance']:.1f}\u2b50",
        f"- **Most active category:** {top_cat}",
        f"- **Most productive source:** {top_src}\n",
        "---\n",
        "## \U0001f5c2 Category Breakdown\n",
    ]

    for cat, cnt in sorted(trends['categories'].items(), key=lambda x: x[1], reverse=True):
        pct = (cnt / total * 100) if total else 0
        lines.append(f"- **{cat.replace('_', ' ').title()}:** {cnt} articles ({pct:.1f}%)")

    lines += ["", "---\n", "## \U0001f4c8 Top Sources\n"]
    for src, cnt in sorted(trends['sources'].items(), key=lambda x: x[1], reverse=True):
        pct = (cnt / total * 100) if total else 0
        lines.append(f"- **{src.replace('_', ' ').title()}:** {cnt} articles ({pct:.1f}%)")

    lines += ["", "---\n", "## \U0001f525 Trending Keywords\n"]
    for kw, cnt in trends['keywords'].most_common(15):
        lines.append(f"- **{kw}:** {cnt} mentions")

    lines += ["", "---\n", "## \U0001f4c5 Daily Activity\n"]
    for d in sorted(trends['daily_counts'], reverse=True):
        day_name = datetime.strptime(d, '%Y-%m-%d').strftime('%A')
        lines.append(f"- **{d} ({day_name}):** {trends['daily_counts'][d]} articles")

    lines += ["", "---\n", "## \U0001f3af Insights & Recommendations\n"]
    if total > 0:
        if trends['daily_counts']:
            best_day = max(trends['daily_counts'], key=trends['daily_counts'].get)
            lines.append(f"- **Most active day:** {datetime.strptime(best_day, '%Y-%m-%d').strftime('%A')} ({best_day})")
        if top_cat:
            lines.append(f"- **Dominant topic:** {top_cat.replace('_', ' ').title()}")
        if trends['avg_relevance'] >= 15:
            lines.append("- **High quality week:** Articles show strong European tech focus")
        elif trends['avg_relevance'] < 10:
            lines.append("- **Consider filter tuning:** Lower than usual relevance scores")
        working = len([s for s in trends['sources'] if s != 'unknown'])
        lines.append(f"- **Source diversity:** {working} active sources contributing content")
    else:
        lines.append("- **No articles processed this week** — check source configurations")

    lines += [
        "", "---\n",
        "## \U0001f517 Quick Links\n",
        "- [Latest Reports](https://github.com/N-Edens/europa-tech-tracker/tree/main/output/daily_reports)",
        "- [Configuration](https://github.com/N-Edens/europa-tech-tracker/blob/main/config/sources.yaml)",
        "- [Project Documentation](https://github.com/N-Edens/europa-tech-tracker#readme)",
        "", "---\n",
        "*Generated by Europa Tech Tracker — Weekly Summary*\n",
    ]

    return "\n".join(lines)


def main():
    days_back = int(os.getenv('DAYS_BACK', '7'))
    print(f"Analysing trends for the past {days_back} days...")

    articles = load_cache_data()
    print(f"Loaded {len(articles)} cached articles")

    trends = analyze_weekly_trends(articles, days_back)
    print(f"Found {trends['total_articles']} articles in analysis period")

    report = generate_summary_report(trends, days_back)
    timestamp = datetime.now().strftime("%Y%m%d")
    report_dir = Path("output/weekly_summaries")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"weekly_summary_{timestamp}.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"Weekly summary saved to: {report_path}")


if __name__ == "__main__":
    main()
