# Europa Tech Tracker

> **Phase 1 MVP** - Basic RSS scraper for European tech news

Automatisk daglig tracker der samler nyheder om europæisk teknologi og alternativer til amerikanske tech-løsninger.

## 🚀 Current Status: Phase 1 MVP

This is the minimal viable product focusing on basic RSS scraping and filtering.

### Features
- ✅ RSS feed parsing fra 2 primære kilder  
- ✅ Basic keyword filtering for europæisk relevans
- ✅ Markdown output til lokale filer
- ✅ Configurable sources via YAML

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper:**
   ```bash
   python src/main.py
   ```

3. **Check output:**
   Results are saved to `output/daily_reports/`

## 📰 Current Sources (Phase 1)

- **Tech.EU** - Leading European startup news
- **Sifted.EU** - European tech and business news  

## 🔧 Configuration

Edit `config/sources.yaml` to modify RSS sources and filtering keywords.

## 📁 Project Structure

```
europa-tech-tracker/
├── src/
│   ├── main.py              # Entry point
│   ├── rss_scraper.py       # RSS feed handling
│   ├── content_filter.py    # Keyword filtering  
│   └── markdown_output.py   # File output
├── config/
│   └── sources.yaml         # RSS sources config
└── output/
    └── daily_reports/       # Generated reports
```

## 🎯 Roadmap

- [x] Phase 1: MVP RSS Scraper
- [ ] Phase 2: Enhanced Processing (categorization, deduplication)
- [ ] Phase 3: GitHub Actions Automation  
- [ ] Phase 4: Google Docs Integration + Advanced Filtering
- [ ] Phase 5: Web Scraping + YouTube Integration

For complete project plan see [PROJECT_PLAN.md](PROJECT_PLAN.md).

## 🔗 Links

- **GitHub Repository:** [N-Edens/europa-tech-tracker](https://github.com/N-Edens/europa-tech-tracker)
- **Google Doc Output:** [Europa Tech Daily Report](https://docs.google.com/document/d/1cn5V7XDPsUgh2l7uUTxGi5Ets5C1FYUI6hQPs5wNgBk/edit)
- **Project Plan:** [Detailed implementation plan](PROJECT_PLAN.md)