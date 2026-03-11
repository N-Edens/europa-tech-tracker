# Phase 4: Google Docs Integration Setup Guide

## 🔗 Overview

Phase 4 adds automatic upload of daily Europa Tech reports to Google Docs, enabling easy sharing and collaborative editing of the daily European tech news summaries.

## ✨ Features

- **Automatic Daily Uploads**: Reports are automatically appended to your Google Docs document
- **Formatted Content**: Clean, readable formatting optimized for Google Docs
- **Statistics & Summaries**: Quick daily statistics and article summaries
- **Top Articles**: Curated list of the highest-relevance European tech articles
- **Timestamp Tracking**: Each report includes generation timestamp
- **Secure Authentication**: Uses OAuth 2.0 for secure API access

## 🔧 Setup Instructions

### Step 1: Install Dependencies

Ensure Google API libraries are installed:

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client` - Google Docs API client
- `google-auth` - Authentication library  
- `google-auth-oauthlib` - OAuth flow handling
- `google-auth-httplib2` - HTTP transport layer

### Step 2: Set Up Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create a new project** or select an existing one
3. **Enable the Google Docs API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Docs API"
   - Click "Enable"

### Step 3: Create OAuth 2.0 Credentials

1. **Go to "APIs & Services" > "Credentials"**
2. **Click "Create Credentials" > "OAuth 2.0 Client ID"**
3. **Configure OAuth consent screen** (if not already done):
   - Choose "External" (unless you have a Google Workspace)
   - Fill in required information:
     - App name: "Europa Tech Tracker"
     - User support email: Your email
     - Developer contact: Your email
4. **Create OAuth 2.0 Client ID**:
   - Application type: **Desktop application**
   - Name: "Europa Tech Tracker Desktop"
5. **Download the credentials JSON file**
6. **Save as**: `config/google_credentials.json`

### Step 4: Prepare Google Docs Document

1. **Create a new Google Docs document** or use the default one
2. **Get the Document ID** from the URL:
   ```
   https://docs.google.com/document/d/[DOCUMENT_ID]/edit
   ```
3. **Update the document ID** in `config/sources.yaml`:
   ```yaml
   google_docs:
     document_id: "YOUR_DOCUMENT_ID_HERE"
   ```

### Step 5: Run Setup Script

Use the automated setup script to verify everything is configured correctly:

```bash
python setup_google_docs.py
```

This script will:
- ✅ Check that dependencies are installed
- ✅ Verify credentials file exists and is valid
- ✅ Test connection to Google Docs API
- ✅ Verify document access permissions
- ✅ Optionally enable Google Docs integration in configuration

### Step 6: Enable Integration

In `config/sources.yaml`, set:

```yaml
google_docs:
  enabled: true  # Enable Google Docs integration
```

## 🚀 Usage

### Automatic Upload

Once configured, Google Docs upload happens automatically:

```bash
python src/main.py
```

The system will:
1. 📡 Collect European tech articles
2. 🔍 Filter and process content  
3. 📄 Generate markdown report
4. 📤 Upload to Google Docs automatically

### Manual Upload Test

To test Google Docs integration manually:

```python
from utils.google_docs import get_google_docs_integration

# Initialize integration
docs = get_google_docs_integration("YOUR_DOCUMENT_ID")

# Test connection
if docs.test_connection():
    print("✅ Google Docs integration working!")
```

### Check Upload Status

The main script logs Google Docs upload status:

```
🔗 Phase 4: Uploading to Google Docs...
✅ Daily report uploaded to Google Docs
📄 Document: Europa Tech Tracker (13 articles)
```

## 📄 Output Format

Daily reports uploaded to Google Docs include:

### Header Section
- 🇪🇺 Report title with date
- 📊 Daily statistics (total articles, relevance scores, sources)
- 🏷️ Top categories and trending keywords

### Articles Section  
- 📰 Top 15 highest-relevance articles
- 🔗 Direct links to original articles
- 📊 Relevance scores and source information
- 🏷️ Category classifications

### Footer
- ⏰ Generation timestamp
- 📈 Session statistics

### Example Output
```
🇪🇺 Europa Tech Daily Report - January 15, 2025

📊 Daily Summary:
• Total European tech articles: 13
• Average relevance score: 18.3⭐
• Active sources: 4
• Top categories: European Companies (5), Startups (4), Cloud (2)

🗞️ Top European Tech Articles:

1. European AI Startup Raises €50M Series B Round
   🔗 https://tech.eu/article/...
   📊 19.2⭐ | 📰 Tech.EU | 🏷️ Startups

2. OVHcloud Launches New European Data Centers
   🔗 https://blog.ovhcloud.com/...
   📊 18.8⭐ | 📰 OVHcloud Blog | 🏷️ Cloud

[... additional articles ...]

---
Generated: 2025-01-15 14:30 UTC
```

## ⚙️ Configuration Options

In `config/sources.yaml`:

```yaml
google_docs:
  enabled: true                    # Enable/disable integration
  document_id: "YOUR_DOC_ID"      # Google Docs document ID
  credentials_path: "config/google_credentials.json"  # OAuth credentials
  upload_daily_reports: true      # Upload daily reports
  upload_weekly_summaries: false  # Upload weekly summaries (future)
  max_articles_per_upload: 15     # Max articles per upload
```

## 🔒 Authentication Flow

### First Run
1. **OAuth browser window opens** automatically
2. **Sign in to Google** account that has access to the document
3. **Grant permissions** to Europa Tech Tracker
4. **Authorization token saved** for future runs

### Subsequent Runs
- **Automatic authentication** using saved token
- **Token refresh** handled automatically
- **No user interaction required**

## 🔧 Troubleshooting

### Common Issues

#### 1. "google-api-python-client not found"
```bash
pip install -r requirements.txt
```

#### 2. "Credentials file not found"
- Download OAuth 2.0 credentials from Google Cloud Console
- Save as `config/google_credentials.json`

#### 3. "Document access denied"
- Check document permissions
- Ensure the Google account has edit access to the document
- Verify the document ID is correct

#### 4. "Authentication failed"
- Delete `config/google_token.json` to reset authentication
- Run the setup script again
- Ensure OAuth consent screen is properly configured

#### 5. "API quota exceeded"
- Google Docs API has usage limits  
- Daily uploads should be well within free tier limits
- Check Google Cloud Console for quota usage

### Enable Debug Logging

For detailed troubleshooting, enable debug logging in your script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Configuration

Run this diagnostic script to test your setup:

```python
# test_google_docs.py
from utils.google_docs import get_google_docs_integration

# Test with your document ID
docs = get_google_docs_integration("YOUR_DOCUMENT_ID")

if docs:
    print("✅ Integration initialized")
    
    if docs.test_connection():
        print("✅ Connection successful")
        
        info = docs.get_document_info()
        print(f"📄 Document: {info['title']}")
    else:
        print("❌ Connection failed")
else:
    print("❌ Integration failed to initialize")
```

## 🔮 Future Enhancements

### Phase 4+ Features
- **Weekly Summaries**: Comprehensive weekly analysis reports
- **Trend Analysis**: Historical trending topics and keywords
- **Multiple Documents**: Support for multiple Google Docs destinations
- **Formatting Options**: Customizable report formatting
- **Collaborative Features**: Integration with Google Docs commenting

## 🆘 Support

### Getting Help

1. **Run the setup script**: `python setup_google_docs.py`
2. **Check the logs** for detailed error messages
3. **Verify all configuration** settings in `sources.yaml`
4. **Test Internet connectivity** and Google API access

### Configuration Files

Key files for Google Docs integration:
- `config/sources.yaml` - Main configuration
- `config/google_credentials.json` - OAuth credentials (download from Google)
- `config/google_token.json` - Authentication token (auto-generated)

### Environment Requirements

- **Python 3.8+**
- **Internet connection** for Google API access
- **Google account** with document access
- **Google Cloud Project** with Docs API enabled

## ✅ Success Criteria

Google Docs integration is working correctly when you see:

```
🔗 Phase 4: Uploading to Google Docs...
✅ Daily report uploaded to Google Docs
📄 Document: Europa Tech Tracker (13 articles)
```

And your Google Docs document contains:
- ✅ Fresh daily report content
- ✅ Properly formatted articles and statistics
- ✅ Current timestamp
- ✅ All links and formatting intact

---

🇪🇺 **Europa Tech Tracker** - *Supporting European digital sovereignty, one news article at a time.*