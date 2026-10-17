import os
import sys
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials/valued-lambda-510909-s8-3b83405326c8.json")

print("=" * 60)
print(" ShopLinx Marketing - Google Integrations Test")
print("=" * 60)

if not os.path.exists(KEY_FILE):
    print(f"[ERROR] Service Account key not found at: {KEY_FILE}")
    sys.exit(1)

print(f"[OK] Found Service Account file: {KEY_FILE}")

# 1. Test Google Search Console (GSC)
print("\n--> Checking Google Search Console (GSC) access...")
try:
    gsc_creds = service_account.Credentials.from_service_account_file(
        KEY_FILE,
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    gsc_service = build("searchconsole", "v1", credentials=gsc_creds)
    sites = gsc_service.sites().list().execute()
    site_entries = sites.get("siteEntry", [])
    if site_entries:
        print(f"[SUCCESS] Connected to GSC! Found {len(site_entries)} site(s):")
        for s in site_entries:
            print(f"  - Site URL: {s.get('siteUrl')} (Permission: {s.get('permissionLevel')})")
    else:
        print("[INFO] GSC connected, but no verified sites found yet for this service account.")
        print("       (Please make sure you added the service account email in GSC Settings > Users & Permissions)")
except Exception as e:
    print(f"[FAIL] GSC Connection Error: {e}")

# 2. Test Google Analytics 4 (GA4)
print("\n--> Checking Google Analytics 4 (GA4) access...")
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    ga4_creds = service_account.Credentials.from_service_account_file(KEY_FILE)
    ga4_client = BetaAnalyticsDataClient(credentials=ga4_creds)
    print("[SUCCESS] GA4 Client initialized successfully!")
except Exception as e:
    print(f"[FAIL] GA4 Initialization Error: {e}")

print("\n" + "=" * 60)
print("Test completed.")
