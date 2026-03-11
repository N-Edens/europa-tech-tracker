"""
Google Docs Integration Module for Europa Tech Tracker
Uses a Service Account for authentication — no browser interaction required.

Setup:
  1. Create a Google Cloud project & enable the Google Docs API
  2. Create a Service Account and download the JSON key
  3. Save the key as  config/google_credentials.json
  4. Share your Google Doc with the service account email (Editor access)
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False


class GoogleDocsIntegration:
    """Handle Google Docs API integration for Europa Tech Tracker."""

    SCOPES = ['https://www.googleapis.com/auth/documents']

    def __init__(self, document_id: str, credentials_path: Optional[str] = None, logger=None):
        if not GOOGLE_LIBS_AVAILABLE:
            raise ImportError("Google API libraries not available. pip install -r requirements.txt")

        self.document_id = document_id
        self.credentials_path = credentials_path or "config/google_credentials.json"
        self.logger = logger
        self.service = None
        self.authenticated = False
        self._authenticate()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    def _authenticate(self):
        """Authenticate via Service Account JSON key."""
        if not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Service account key not found: {self.credentials_path}\n"
                "Download it from Google Cloud Console → IAM → Service Accounts."
            )

        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES
            )
            self.service = build('docs', 'v1', credentials=creds)
            self.authenticated = True
            if self.logger:
                self.logger.debug("Google Docs API authenticated (service account)")
        except Exception as e:
            self.authenticated = False
            if self.logger:
                self.logger.error(f"Google Docs authentication failed: {e}")
            raise

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------
    def test_connection(self) -> bool:
        if not self.authenticated:
            return False
        try:
            doc = self.service.documents().get(documentId=self.document_id).execute()
            if self.logger:
                self.logger.debug(f"Connected to document: '{doc.get('title')}'")
            return True
        except HttpError as e:
            if self.logger:
                self.logger.error(f"Document access failed: {e}")
            return False

    def get_document_info(self) -> Dict[str, Any]:
        if not self.authenticated:
            raise RuntimeError("Not authenticated")
        doc = self.service.documents().get(documentId=self.document_id).execute()
        return {
            'title': doc.get('title', 'Untitled'),
            'document_id': self.document_id,
            'revision_id': doc.get('revisionId'),
        }

    # ------------------------------------------------------------------
    # Writing content
    # ------------------------------------------------------------------
    def append_daily_report(self, report_text: str, articles: List[Dict], date: str = None) -> bool:
        """Append a plain-text daily report at the end of the document."""
        if not self.authenticated:
            return False

        date = date or datetime.now().strftime('%Y-%m-%d')

        try:
            # Build the full text block to insert
            body = self._build_report_text(articles, date)

            # Find end-of-document index
            doc = self.service.documents().get(documentId=self.document_id).execute()
            end_index = self._get_end_index(doc)

            # Single insertText request — simple and reliable
            requests = [{
                'insertText': {
                    'location': {'index': end_index},
                    'text': body,
                }
            }]

            self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests},
            ).execute()

            if self.logger:
                self.logger.info(f"Report for {date} appended to Google Docs")
            return True

        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to append report: {e}")
            return False

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _get_end_index(doc: dict) -> int:
        """Return the last valid insertion index in *doc*."""
        end = 1
        for elem in doc.get('body', {}).get('content', []):
            if 'endIndex' in elem:
                end = max(end, elem['endIndex'])
        return max(1, end - 1)

    def _build_report_text(self, articles: List[Dict], date: str) -> str:
        """Build the plain-text report that gets inserted into Google Docs."""
        lines: list[str] = []

        separator = "\n" + "=" * 60 + "\n"
        lines.append(separator)
        lines.append(f"\U0001F1EA\U0001F1FA Europa Tech Daily Report — {date}\n")

        # Summary stats
        if articles:
            total = len(articles)
            avg = sum(a.get('relevance_score', 0) for a in articles) / total

            cats: dict[str, int] = {}
            srcs: dict[str, int] = {}
            for a in articles:
                cat = a.get('primary_category', 'uncategorized')
                cats[cat] = cats.get(cat, 0) + 1
                src = a.get('source', 'unknown')
                srcs[src] = srcs.get(src, 0) + 1

            top_cats = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:3]
            top_srcs = sorted(srcs.items(), key=lambda x: x[1], reverse=True)[:3]

            lines.append("")
            lines.append("\U0001F4CA Summary")
            lines.append(f"  Total articles: {total}")
            lines.append(f"  Avg relevance:  {avg:.1f}")
            lines.append(f"  Top categories: {', '.join(f'{k} ({v})' for k, v in top_cats)}")
            lines.append(f"  Top sources:    {', '.join(f'{k} ({v})' for k, v in top_srcs)}")
        else:
            lines.append("\nNo European tech articles found today.")

        # Article list
        lines.append("")
        lines.append("\U0001F5DE Top European Tech Articles\n")

        sorted_articles = sorted(articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        for i, a in enumerate(sorted_articles[:15], 1):
            title = a.get('title', 'No title')
            url = a.get('url', a.get('link', ''))
            src = a.get('source', '').replace('_', ' ').title()
            rel = a.get('relevance_score', 0)
            cat = a.get('primary_category', '').replace('_', ' ').title()

            lines.append(f"  {i}. {title}")
            if url:
                lines.append(f"     {url}")
            lines.append(f"     {rel:.0f}\u2B50 | {src} | {cat}")
            lines.append("")

        lines.append(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")

        return "\n".join(lines)


# ------------------------------------------------------------------
# Factory / convenience
# ------------------------------------------------------------------
def get_google_docs_integration(document_id: str, logger=None) -> Optional[GoogleDocsIntegration]:
    """Create and return a ready-to-use GoogleDocsIntegration, or None on failure."""
    try:
        integration = GoogleDocsIntegration(document_id, logger=logger)
        if integration.test_connection():
            if logger:
                logger.info("\u2705 Google Docs integration ready")
            return integration
        if logger:
            logger.warning("Google Docs connection test failed — check document sharing")
        return None
    except ImportError:
        if logger:
            logger.warning("Google Docs disabled: missing dependencies (pip install -r requirements.txt)")
        return None
    except FileNotFoundError as e:
        if logger:
            logger.warning(f"Google Docs disabled: {e}")
        return None
    except Exception as e:
        if logger:
            logger.error(f"Google Docs integration failed: {e}")
        return None


def setup_google_docs_credentials():
    """Print step-by-step setup instructions."""
    print("""
\U0001F527 Google Docs Integration — Setup Guide (Service Account)

1. Go to https://console.cloud.google.com/
2. Create (or select) a project.
3. Enable the "Google Docs API":
     APIs & Services  >  Library  >  search "Google Docs API"  >  Enable
4. Create a Service Account:
     IAM & Admin  >  Service Accounts  >  Create Service Account
     - Name: europa-tech-tracker
     - Role: (skip — not needed)
     - Click Done
5. Create a key for the service account:
     Click the service account  >  Keys  >  Add Key  >  Create new key  >  JSON
6. Save the downloaded JSON file as:
     config/google_credentials.json
7. Open your Google Doc and share it (Editor) with the service account email.
   The email looks like:  europa-tech-tracker@PROJECT.iam.gserviceaccount.com

Your Google Doc ID: 1cn5V7XDPsUgh2l7uUTxGi5Ets5C1FYUI6hQPs5wNgBk
""")


if __name__ == "__main__":
    setup_google_docs_credentials()