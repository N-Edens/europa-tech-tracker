# Europa Tech News Tracker — Projektplan

**Automatisk daglig nyhedstracker for europæisk teknologi og alternativer til amerikanske tech-løsninger**

---

## 🎯 Projektmål

Udvikle en automatiseret løsning der hver dag indsamler og organiserer nyheder om:
- Europæiske tech-selskaber og startups
- EU-tech politikker og initiativer
- Open source alternativer til amerikanske tech-giganter
- Europæiske cloud-løsninger (alternativer til AWS/Azure)
- Privacy-fokuserede tjenester fra Europa
- Europæisk AI, cybersikkerhed og innovation

---

## 🚀 Faseopdelt Implementering

### 📋 Fase Oversigt
```
Fase 1: MVP - Basic RSS Scraper (1-2 uger) ✅ COMPLETED
├── Simpel RSS-indsamling fra 2-3 kilder
├── Basic filtrering og markdown output
└── Manuel kørsel

Fase 2: Enhanced Processing (1-2 uger) ✅ COMPLETED
├── Flere nyhedskilder
├── Kategorisering og deduplicering
└── Lokal caching system

Fase 3: Automation & GitHub Integration (1 uge) ✅ COMPLETED
├── GitHub Actions workflow
├── Daglig automatisk kørsel
└── Basic error handling

Fase 4: Advanced Features (2-3 uger) ✅ COMPLETED
├── Google Docs integration ✅
├── Comprehensive test suite ✅
├── Production validation ✅
└── Setup documentation ✅

Fase 5: Polish & Scale (1-2 uger) 🔄 NEXT
├── Web scraping (ikke-RSS kilder)
├── YouTube integration
├── Weekly summaries og analytics
└── Anti-US filtering improvements
```

### 🏃‍♂️ Fase 1: MVP - Basic RSS Scraper ✅ COMPLETED
**Mål:** Få en fungerende prototype med minimal functionality
**Varighed:** 1-2 uger
**Status:** ✅ Completed

#### Leverancer:
- [x] Basic projektstruktur 
- [x] RSS scraper for tech.eu og sifted.eu
- [x] Simple keyword filtering (Cloud, Privacy, EU Policy)
- [x] Markdown output til lokale filer  
- [x] Requirements.txt og basic configuration

#### Acceptkriterier:
- ✅ Kan hente artikler fra 2 RSS feeds
- ✅ Filtrerer artikler baseret på europæiske keywords
- ✅ Gemmer resultat i markdown format
- ✅ Kan køres manuelt fra kommandolinje

#### Teknisk scope:
```
europa-tech-tracker/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py                 # MVP entry point
│   ├── rss_scraper.py         # Basic RSS functionality
│   ├── content_filter.py      # Simple keyword matching
│   └── markdown_output.py     # Local file output
├── config/
│   └── sources.yaml           # 2-3 RSS kilder
└── output/
    └── daily_reports/         # Local markdown files
```

---

### 🔧 Fase 2: Enhanced Processing ✅ COMPLETED
**Mål:** Forbedr datakvalitet og tilføj flere kilder
**Varighed:** 1-2 uger
**Status:** ✅ Completed

#### Leverancer:
- [x] Udvidet til 5-7 RSS kilder
- [x] Auto-kategorisering (Cloud, Privacy, EU Policy, Startups, Open Source)
- [x] Deduplicering baseret på URL og titel-lighed
- [x] JSON-baseret caching system
- [x] Forbedret konfigurationssystem

#### Acceptkriterier:
- ✅ Støtter 5+ RSS kilder
- ✅ Automatisk kategorisering med 80%+ nøjagtighed  
- ✅ Eliminerer duplicate artikler effektivt
- ✅ Cache bevarer state mellem kørsler
- ✅ Konfigurerbart via YAML filer

#### Teknisk udvidelser:
```python
# config/sources.yaml struktur
sources:
  tech_eu:
    url: "https://tech.eu/feeds/" 
    priority: high
    categories: ["startups", "cloud", "policy"]
  
  sifted_eu:
    url: "https://sifted.eu/feed/"
    priority: high
    categories: ["startups", "funding"]
```

---

### ⚙️ Fase 3: Automation & GitHub Integration ✅ COMPLETED
**Mål:** Automatiser med GitHub Actions
**Varighed:** 1 uge  
**Status:** ✅ Completed

#### Leverancer:
- [x] GitHub Actions workflow for daglig kørsel
- [x] Manuel trigger capability
- [x] Basic error handling og logging
- [x] Commit caching data tilbage til repository  

#### Acceptkriterier:
- ✅ Kører automatisk hver dag kl 07:00 Copenhagen tid
- ✅ Håndterer fejl elegant uden at crashe
- ✅ Gemmer cache og output tilbage til GitHub
- ✅ Kan trigges manuelt ved behov

#### GitHub Actions struktur:
```yaml
# .github/workflows/daily_tracker.yml
name: Europa Tech Daily Tracker
on:
  schedule:
    - cron: "0 6 * * *"  # 07:00 Copenhagen tid
  workflow_dispatch:

jobs:
  collect_news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python 3.9
        uses: actions/setup-python@v4
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run news collection
        run: python src/main.py
      - name: Commit results
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data/ output/
          git commit -m "Daily news update $(date)" || exit 0
          git push
```

---

### 🎯 Fase 4: Advanced Features ✅ COMPLETED
**Mål:** Tilføj avancerede funktioner og integrations
**Varighed:** 2-3 uger
**Status:** ✅ Completed January 2025

#### Leverancer:
- [x] Google Docs integration med OAuth 2.0 authentication
- [x] Comprehensive test suite (unit, integration, workflow tests)
- [x] Automated testing via GitHub Actions
- [x] Production system validation
- [x] Setup documentation og troubleshooting guide

#### Acceptkriterier:
- ✅ Opdaterer Google Doc automatisk hver dag
- ✅ Robust test coverage for all phases
- ✅ Production-ready authentication system
- ✅ Comprehensive setup documentation

#### Google Docs integration:
```python 
# Implementeret features:
IMPLEMENTED_FEATURES = [
    "OAuth 2.0 authentication",
    "Automatic daily report upload", 
    "Document access verification",
    "Formatted content for Google Docs",
    "Setup script and documentation"
]
```

#### Test Suite:
- ✅ Unit tests for all core components
- ✅ Integration tests for end-to-end workflows  
- ✅ GitHub Actions automated testing
- ✅ Test fixtures and mock systems
- ✅ Coverage reporting

---

### 🌟 Fase 5: Polish & Scale
**Mål:** Final features og optimering
**Varighed:** 1-2 uger

#### Leverancer:
- [ ] Web scraping for ikke-RSS kilder (EU official sites)
- [ ] YouTube integration for video content
- [ ] Weekly trend analysis og summaries
- [ ] Performance optimering
- [ ] Comprehensive documentation

#### Acceptkriterier:
- Støtter web scraping ud over RSS
- Inkluderer relevant YouTube content
- Genererer ugentlige trend rapporter
- Fuld dokumentation for maintenance 

---

### 📅 Implementation Timeline

```
│ Uge 1-2  │ Fase 1: MVP RSS Scraper              │ ✅ COMPLETED
│ Uge 3-4  │ Fase 2: Enhanced Processing          │ ✅ COMPLETED
│ Uge 5    │ Fase 3: GitHub Actions Automation    │ ✅ COMPLETED
│ Uge 6-8  │ Fase 4: Advanced Features            │ ✅ COMPLETED
│ Uge 9-10 │ Fase 5: Polish & Scale               │ 🔄 NEXT
│ Uge 11   │ Testing & Documentation              │ 🔄 ONGOING
```

**Total estimeret tid: 10-11 uger**
**Aktuelt: Uge 8-9 (Januar 2025)**

### 🎯 Success Metrics per Fase:
- **Fase 1:** ✅ Fungerende lokalt system med 2 kilder
- **Fase 2:** ✅ 5+ kilder med kategorisering og caching  
- **Fase 3:** ✅ Fuldt automatiseret daglig kørsel
- **Fase 4:** ✅ Google Docs integration + comprehensive test suite
- **Fase 5:** 🔄 Production-ready med alle features

### 📊 Current System Status (January 2025):
- **Active Sources**: 6 RSS feeds (4 working, 2 with issues)
- **Daily Processing**: ~40 articles → ~13 European tech articles
- **Average Relevance**: 18.3⭐ score
- **Test Coverage**: Comprehensive suite with CI/CD
- **Google Docs**: Ready for integration (dependencies documented)
- **Production Ready**: ✅ Validated outside test environment

---

## 🏗️ System Arkitektur

### Core Components
1. **GitHub Actions Workflow** - Automatisk daglig kørsel
2. **Multi-Source News Scraper** - Python script med avanceret filtrering
3. **Content Processor** - Kategorisering og deduplicering
4. **Output Handler** - Google Doc eller alternativ output
5. **Configuration Management** - Nem opdatering af søgetermer og kilder

### Teknisk Stack
- **Python 3.9+** - Core scraping og processing
- **GitHub Actions** - Automatisering og scheduling
- **Google APIs** - Docs og YouTube integration
- **RSS/API integration** - Multiple nyhedskilder
- **JSON storage** - Cache og deduplicering

---

## 📰 Nyhedskilder (Prioriteret liste)

### Tier 1 - Primære europæiske tech-medier
```yaml
- tech_eu:
    url: "https://tech.eu/feeds/"
    type: "rss"
    priority: "high"
    
- sifted_eu:
    url: "https://sifted.eu/feed/"
    type: "rss"
    priority: "high"
    
- the_next_web:
    url: "https://thenextweb.com/feed/"
    type: "rss"
    priority: "medium"
    filter: "europe, european"
```

### Tier 2 - Officielle EU/regering kilder
```yaml
- eu_digital_single_market:
    url: "https://digital-strategy.ec.europa.eu/en"
    type: "web_scrape"
    priority: "medium"
    
- european_innovation_council:
    url: "https://eic.ec.europa.eu/news_en"
    type: "web_scrape"
    priority: "medium"
```

### Tier 3 - Tech-selskaber og organisationer
```yaml
- ovhcloud_blog:
    url: "https://blog.ovhcloud.com/feed/"
    type: "rss"
    priority: "medium"
    
- sap_news:
    url: "https://news.sap.com/feed/"
    type: "rss"
    priority: "low"
```

---

## 🔍 Søgetermer & Kategorier

### Kategorier og associerede søgetermer

#### 🌥️ Cloud & Infrastructure
```python
CLOUD_TERMS = [
    # Europæiske cloud-udbydere
    "OVHcloud", "Scaleway", "Hetzner Cloud", "IONOS", "UpCloud",
    "European cloud", "European hosting", "GDPR compliant cloud",
    
    # Alternativer til AWS/Azure
    "AWS alternative", "Azure alternative", "European data centers",
    "Data sovereignty", "European hosting providers"
]
```

#### 🔒 Privacy & Security
```python
PRIVACY_TERMS = [
    "European privacy tech", "GDPR compliance", "Data protection",
    "Privacy by design", "European cybersecurity", "Zero knowledge",
    "End-to-end encryption", "Privacy-first", "Data sovereignty",
    "Nextcloud", "Signal", "ProtonMail", "Matrix protocol"
]
```

#### 🏛️ EU Tech Policy
```python
POLICY_TERMS = [
    "Digital Markets Act", "Digital Services Act", "GDPR",
    "AI Act", "European AI regulation", "Tech sovereignty",
    "Digital Europe Programme", "Horizon Europe", "EIC Accelerator",
    "European Chips Act", "Digital Compass"
]
```

#### 🚀 Startups & Innovation
```python
STARTUP_TERMS = [
    "European startup", "European unicorn", "European tech funding",
    "EIC Accelerator", "European Innovation Council", "Horizon Europe",
    "European VC", "European tech ecosystem", "Digital Europe startup"
]
```

#### 🛠️ Open Source & Alternatives
```python
OPENSOURCE_TERMS = [
    "Open source alternative", "European open source", "FOSS",
    "LibreOffice", "Nextcloud", "GitLab EU", "European Linux",
    "Open source cloud", "European developer tools"
]
```

---

## 📁 Project Structure

```
europa-tech-tracker/
├── README.md
├── PROJECT_PLAN.md                    # Dette dokument
├── requirements.txt
├── .gitignore
├── config/
│   ├── sources.yaml                   # Nyhedskilder konfiguration
│   ├── search_terms.yaml              # Søgetermer per kategori
│   └── filters.yaml                   # Content filtering regler
├── src/
│   ├── main.py                        # Entry point
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py            # Base scraper klasse
│   │   ├── rss_scraper.py             | RSS/Atom feeds
│   │   ├── web_scraper.py             # Web scraping
│   │   ├── api_scraper.py             # API-baserede kilder
│   │   └── youtube_scraper.py         # YouTube integration
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── content_filter.py          # Anti-US tech filter
│   │   ├── categorizer.py             # Auto-kategorisering
│   │   ├── deduplicator.py            # Duplicate detection
│   │   └── sentiment.py               # Sentiment analyse
│   ├── outputs/
│   │   ├── __init__.py
│   │   ├── google_docs.py             # Google Docs integration
│   │   ├── markdown.py                # Markdown output
│   │   └── email.py                   # Email digest (fremtidig)
│   └── utils/
│       ├── __init__.py
│       ├── cache.py                   # Cache management
│       ├── config_loader.py           # Configuration loading
│       └── logger.py                  # Logging utilities
├── data/
│   ├── cache/
│   │   ├── seen_urls.json             # URL deduplication
│   │   └── article_cache.json         # Article caching
│   └── output/
│       └── daily_reports/             # Local reports backup
├── .github/
│   └── workflows/
│       ├── daily_tracker.yml          # Daglig automatisk kørsel
│       ├── manual_run.yml             # Manuel trigger
│       └── weekly_summary.yml         # Ugentligt sammendrag
└── tests/
    ├── __init__.py
    ├── test_scrapers.py
    ├── test_processors.py
    └── test_integration.py
```

---

## 🔄 Workflow & Automation

### Daglig Workflow (07:00 Copenhagen tid)
```yaml
name: "Europa Tech Daily Tracker"
on:
  schedule:
    - cron: "0 6 * * *"  # 07:00 Copenhagen (UTC+1/+2)
  workflow_dispatch:     # Manuel trigger

jobs:
  track_europa_tech:
    steps:
      1. Checkout repository
      2. Setup Python environment
      3. Install dependencies
      4. Run news collection
      5. Process and filter content
      6. Generate daily report
      7. Update Google Doc
      8. Commit changes to cache
```

### Weekly Summary (Søndag aften)
```yaml
name: "Europa Tech Weekly Summary"
on:
  schedule:
    - cron: "0 20 * * 0"  # Søndag 21:00 Copenhagen

jobs:
  weekly_summary:
    steps:
      1-4. [Same as daily]
      5. Generate weekly trending topics
      6. Create summary report
      7. Send email digest (optional)
```

---

## ⚙️ Konfiguration & Secrets

### GitHub Secrets (Required)
```yaml
GOOGLE_CREDENTIALS_JSON: "Service account JSON fra Google Cloud Console"
GOOGLE_DOC_ID: "ID fra Google Doc URL"
YOUTUBE_API_KEY: "YouTube Data API v3 key"
```

### Environment Variables (Optional)
```yaml
FILTER_SENSITIVITY: "0.7"        # Anti-US filter følsomhed (0-1)
MAX_ARTICLES_PER_DAY: "50"       # Max artikler per dag
ENABLE_SENTIMENT: "true"         # Aktiver sentiment analyse
OUTPUT_FORMAT: "google_docs"     # Output format
```

### Configuration Files
- **sources.yaml** - Nyhedskilder med prioriteter og filtre
- **search_terms.yaml** - Søgetermer organiseret efter kategorier
- **filters.yaml** - Regler til at filtrere amerikanske tech-nyheder fra

---

## 📊 Content Processing Pipeline

### 1. Collection Phase
```python
for source in enabled_sources:
    articles = scraper.fetch(source)
    raw_articles.extend(articles)
```

### 2. Filtering Phase
```python
# Anti-amerikansk tech filter
filtered_articles = anti_us_filter(raw_articles)

# Relevant content filter
relevant_articles = relevance_filter(filtered_articles, search_terms)
```

### 3. Enhancement Phase
```python
for article in relevant_articles:
    article.category = categorizer.classify(article)
    article.sentiment = sentiment_analyzer.analyze(article)
    article.european_alternative = find_alternatives(article)
```

### 4. Deduplication
```python
unique_articles = deduplicator.remove_duplicates(
    enhanced_articles, 
    cache.seen_urls
)
```

### 5. Output Generation
```python
daily_report = report_generator.create_daily_report(unique_articles)
google_docs.append_to_doc(daily_report)
```

---

## 🎛️ Anti-US Tech Filter

### Filter Kriterier
```python
US_TECH_KEYWORDS = [
    "Amazon", "AWS", "Microsoft Azure", "Google Cloud",
    "Meta", "Facebook", "Apple", "Netflix", "Uber",
    "Silicon Valley", "FAANG", "Big Tech"
]

US_FOCUSED_PHRASES = [
    "US market expansion",
    "American tech dominance", 
    "Silicon Valley startup",
    "US venture capital"
]
```

### Positive Europa Boost
```python
EUROPA_BOOST_KEYWORDS = [
    "European alternative", "GDPR compliant", "Data sovereignty",
    "European startup", "EU regulation", "Privacy-first",
    "Open source", "European cloud"
]
```

---

## 🚀 Implementation Phases

### Phase 1: MVP (Minimal Viable Product) - Uge 1
- [ ] Basic project struktur
- [ ] Simple RSS scraper for 5 hovedkilder
- [ ] Basic Google Docs integration
- [ ] GitHub Actions setup
- [ ] Manual kategorisering

### Phase 2: Enhanced Filtering - Uge 2
- [ ] Anti-US tech filter implementation
- [ ] Automatic kategorisering
- [ ] Deduplication system
- [ ] Improved search terms

### Phase 3: Multi-Source Integration - Uge 3
- [ ] Web scraping for officielle kilder
- [ ] YouTube integration
- [ ] API integration for tech-selskaber
- [ ] Sentiment analyse

### Phase 4: Advanced Features - Uge 4
- [ ] Weekly summary reports
- [ ] Trend detection
- [ ] Email digest option
- [ ] European alternatives matching
- [ ] Performance optimization

### Phase 5: Production Ready - Uge 5
- [ ] Comprehensive testing
- [ ] Error handling og logging
- [ ] Documentation
- [ ] Monitoring og alerts
- [ ] Configuration management

---

## 📝 Manual Tasks & Maintenance

### Weekly Review (Manual)
- [ ] Review nye europæiske tech-selskaber at følge
- [ ] Opdater search terms baseret på trending topics
- [ ] Check for nye nyhedskilder
- [ ] Review filter effectiveness

### Monthly Optimization
- [ ] Analyse mest populære kategorier
- [ ] Opdater nyhedskilder prioriteter
- [ ] Review og rens cache
- [ ] Performance monitorering

---

## 🎯 Success Metrics

### Daily Targets
- 15-30 relevante artikler per dag
- < 5% duplicates
- 80%+ europæisk fokus (anti-US filter effectiveness)
- 90%+ uptime på automated runs

### Weekly Analysis
- Trending europæiske tech topics
- New European tech companies discovered
- Alternative solutions identified
- Community engagement (hvis offentliggjort)

---

## 🔮 Future Expansions

### Next Features (efter Phase 5)
- **Slack/Discord integration** - Real-time notifications
- **European tech stocks tracking** - Kombiner med financial data
- **Podcast integration** - European tech podcasts
- **Translation service** - Auto-translate non-engelsk content
- **AI summary generation** - GPT integration for summaries
- **Community contributions** - Allow suggestions for new sources

### European Alternative Database
- Buildet database over europæiske alternativer til amerikanske tjenester
- Automatisk matching af nyheder med relevante alternativer
- API for andre projekterer at bruge

---

## 📞 Next Steps

1. **Gennemgå denne plan** og tilpas efter feedback
2. **Setup GitHub repository** med initial struktur
3. **Implementer Phase 1 MVP** med basic functionality
4. **Test med 1 uge manual kørsel** for at validere approach
5. **Iterér baseret på resultater** og gå videre til Phase 2

---

*Sidst opdateret: 15. januar 2025*
*Status: Fase 4 completed ✅ - Google Docs integration ready, comprehensive test suite implemented*
*Næste: Fase 5 - Web scraping, YouTube integration, og advanced analytics*