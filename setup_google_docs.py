#!/usr/bin/env python3
"""
Google Docs Integration Setup Script for Europa Tech Tracker
Uses Service Account authentication — no browser interaction required.
"""

import os
import sys
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def check_dependencies():
    """Check if Google API dependencies are installed."""
    try:
        import google.oauth2.service_account  # noqa: F401
        import googleapiclient.discovery       # noqa: F401
        print("✅ Google API dependencies installed")
        return True
    except ImportError:
        print("❌ Google API dependencies missing")
        print("   Run:  pip install -r requirements.txt")
        return False


def check_credentials_file():
    """Validate the service-account key file."""
    path = "config/google_credentials.json"
    if not os.path.exists(path):
        print(f"❌ Service-account key not found: {path}")
        return False

    try:
        with open(path, 'r') as f:
            data = json.load(f)

        if data.get('type') == 'service_account':
            email = data.get('client_email', '???')
            print(f"✅ Service-account key valid  ({email})")
            print(f"   ⚠️  Make sure your Google Doc is shared with this email (Editor)!")
            return True
        else:
            print(f"❌ Expected type 'service_account', got '{data.get('type')}'")
            print("   Download a Service Account JSON key, not an OAuth client ID.")
            return False
    except json.JSONDecodeError:
        print("❌ File is not valid JSON")
        return False


def test_connection():
    """Try to read the Google Doc via the API."""
    from utils.google_docs import GoogleDocsIntegration

    doc_id = "1cn5V7XDPsUgh2l7uUTxGi5Ets5C1FYUI6hQPs5wNgBk"
    print(f"\n🔗 Testing connection to document {doc_id[:12]}…")

    try:
        integration = GoogleDocsIntegration(doc_id)
        if integration.test_connection():
            info = integration.get_document_info()
            print(f"✅ Connected!  Document title: \"{info['title']}\"")
            return integration
        else:
            print("❌ Could not access the document.")
            print("   → Share the document with the service-account email (Editor access).")
            return None
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return None
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def send_test_report(integration):
    """Send a small test report so the user can see it in their doc."""
    from datetime import datetime

    test_articles = [
        {
            'title': 'Europa Tech Tracker — forbindelse bekræftet!',
            'url': 'https://github.com/N-Edens/europa-tech-tracker',
            'source': 'setup_script',
            'relevance_score': 99,
            'primary_category': 'test',
        }
    ]

    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    success = integration.append_daily_report("test", test_articles, date)
    if success:
        print("✅ Test-rapport sendt til Google Docs — tjek dokumentet!")
    else:
        print("❌ Kunne ikke skrive til dokumentet.")
    return success


def main():
    print("🔧 Europa Tech Tracker — Google Docs Setup (Service Account)")
    print("=" * 62)

    # 1. Dependencies
    print("\n1️⃣  Dependencies")
    if not check_dependencies():
        sys.exit(1)

    # 2. Credentials file
    print("\n2️⃣  Service-account key")
    if not check_credentials_file():
        print("""
📋 Sådan opretter du en Service Account:
   1. Gå til https://console.cloud.google.com/
   2. Opret eller vælg et projekt
   3. Aktivér "Google Docs API"  (APIs & Services → Library)
   4. Gå til IAM & Admin → Service Accounts → Create Service Account
      - Navn: europa-tech-tracker
   5. Klik på den nye service account → Keys → Add Key → JSON
   6. Gem filen som:  config/google_credentials.json
   7. Del dit Google Doc med service-account-emailen (Editor)
""")
        sys.exit(1)

    # 3. Connection test
    print("\n3️⃣  Connection")
    integration = test_connection()
    if not integration:
        sys.exit(1)

    # 4. Send test report
    print("\n4️⃣  Sending test report")
    send_test_report(integration)

    print("\n🎉 Setup fuldført!  Kør 'python src/main.py' for at sende rigtige rapporter.")


if __name__ == "__main__":
    main()