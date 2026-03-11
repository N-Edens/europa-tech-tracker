# 🤖 Europa Tech Tracker Workflows

This directory contains GitHub Actions workflows for automated news tracking and analysis.

## 📅 Workflow Schedule

| Workflow | Schedule | Purpose | Manual Trigger |
|----------|----------|---------|----------------|
| **Daily Tracker** | Mon-Fri 07:00 CET | Collect and analyze daily news | ✅ Available |
| **Weekly Summary** | Sunday 21:00 CET | Generate weekly trend reports | ✅ Available |
| **Manual Run** | On-demand | Testing and debugging | ✅ Primary purpose |

## 📋 Workflow Details

### 🔄 Daily Tracker (`daily_tracker.yml`)

**Purpose:** Automated daily collection of European tech news

**Runs:** Monday through Friday at 07:00 Copenhagen time (06:00/05:00 UTC)

**Process:**
1. 📥 Checkout repository with full history
2. 🐍 Setup Python 3.11 environment 
3. 📦 Install dependencies with pip cache
4. 📡 Collect articles from RSS sources
5. 🧠 Process and filter European content
6. 📊 Generate daily markdown report
7. 💾 Auto-commit results and cache
8. 📈 Create GitHub Actions summary

**Outputs:**
- Daily reports: `output/daily_reports/europa_tech_YYYYMMDD.md`
- Updated cache: `data/cache/article_cache.json`
- Session logs: `logs/session_YYYYMMDD_HHMMSS.log`

**Manual Parameters:**
- `test_mode`: Run without committing
- `cleanup_cache`: Clean old cache entries
- `debug_level`: Control logging verbosity

### 📊 Weekly Summary (`weekly_summary.yml`)

**Purpose:** Generate comprehensive weekly trend analysis

**Runs:** Every Sunday at 21:00 Copenhagen time (20:00 UTC)

**Process:**
1. 📥 Checkout with full history
2. 🐍 Setup Python environment + visualization libs
3. 📊 Analyze past week's cached articles
4. 📈 Generate trend and category breakdowns
5. 🔥 Identify trending keywords and topics
6. 📄 Create detailed weekly report
7. 💾 Commit summary to repository
8. 📧 Create GitHub issue with summary

**Analysis Features:**
- Category distribution analysis
- Source performance metrics  
- Keyword trending analysis
- Daily activity patterns
- Quality insights and recommendations

**Manual Parameters:**
- `days_back`: Period to analyze (default: 7)
- `include_trends`: Enable trend analysis

### 🛠️ Manual Run (`manual_run.yml`)

**Purpose:** On-demand testing and debugging with full control

**Trigger:** Manual workflow dispatch only

**Features:**
- **Test Mode:** Run without committing changes
- **Custom Sources:** Override default source configuration
- **Debug Levels:** Control logging detail (DEBUG/INFO/WARNING)
- **Cache Management:** Clean cache before/after runs
- **Artifact Upload:** Download logs and outputs

**Use Cases:**
- Testing new RSS sources before adding to config
- Debugging processing issues with detailed logs
- Running analysis on custom date ranges
- Validating changes before automated deployment

**Manual Parameters:**
- `test_mode`: Prevent commits (default: true)
- `debug_level`: Logging verbosity
- `custom_sources`: Override sources temporarily
- `cleanup_cache`: Cache maintenance options
- `upload_artifacts`: Save logs and outputs

## 🔧 Configuration Files

### Dependencies (`requirements.txt`)
```
feedparser>=6.0.10
beautifulsoup4>=4.12.0
requests>=2.31.0
PyYAML>=6.0
```

### Sources (`config/sources.yaml`)
- RSS feed URLs and configurations
- Keyword filters for European relevance
- Source categorization settings
- Rate limiting and timeout configurations

## 📊 Output Structure

```
output/
├── daily_reports/          # Daily markdown reports
│   └── europa_tech_YYYYMMDD.md
├── weekly_summaries/       # Weekly trend analyses  
│   └── weekly_summary_YYYYMMDD.md
├── data/                   # Cache and processed data
│   └── cache/
│       └── article_cache.json
└── logs/                   # Session and debug logs
    └── session_YYYYMMDD_HHMMSS.log
```

## 🚀 Getting Started

### 1. Trigger Manual Run
Test the system with the Manual Run workflow:
- Go to Actions → Manual Run workflow
- Enable test mode (default)
- Set debug level to DEBUG for detailed logs
- Review artifacts after completion

### 2. Monitor Daily Runs
Daily tracker runs automatically on weekdays:
- Check Actions tab for workflow status
- Review daily reports in `output/daily_reports/`
- Monitor cache growth in `data/cache/`

### 3. Weekly Reviews
Every Sunday, review the weekly summary:
- Trend analysis in `output/weekly_summaries/`
- GitHub issue created with key metrics
- Source performance evaluation

## 🐛 Troubleshooting

### Common Issues

**Workflow failing to start:**
- Check cron timezone (UTC vs local)
- Verify repository permissions
- Ensure workflows are enabled

**No articles collected:**
- Check RSS source availability
- Review source configuration in `config/sources.yaml`
- Enable DEBUG logging in Manual Run

**Low relevance scores:**
- Review keyword filters
- Check source quality and language
- Adjust relevance scoring algorithm

**Cache issues:**
- Clear cache using Manual Run cleanup options
- Check JSON format validity
- Monitor disk space usage

### Debug Steps

1. **Run Manual workflow** with DEBUG logging
2. **Download artifacts** to review detailed logs  
3. **Check source configuration** for 403/404 errors
4. **Validate JSON cache** for corruption
5. **Review recent commits** for processing changes

## 🔗 Links

- [Main Repository](https://github.com/N-Edens/europa-tech-tracker)
- [Daily Reports](../output/daily_reports/)
- [Configuration](../config/sources.yaml)
- [Project Documentation](../README.md)

---

*Automated European tech news tracking with GitHub Actions* 🇪🇺🤖