import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SITE_URL = os.getenv("GSC_SITE_URL", "https://www.shoplinx.ai/")

def fetch_gsc_queries(days=30):
    creds = service_account.Credentials.from_service_account_file(
        KEY_FILE, scopes=["https://www.googleapis.com/auth/webmasters.readonly"]
    )
    service = build("searchconsole", "v1", credentials=creds)

    request = {
        "startDate": "2026-09-01",
        "endDate": "2026-10-06",
        "dimensions": ["query", "page"],
        "rowLimit": 250
    }
    response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
    rows = response.get("rows", [])
    
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/gsc_performance.csv"
    
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query", "Page", "Clicks", "Impressions", "CTR (%)", "Average Position"])
        for r in rows:
            writer.writerow([
                r["keys"][0],
                r["keys"][1],
                r["clicks"],
                r["impressions"],
                f"{r['ctr'] * 100:.2f}",
                f"{r['position']:.1f}"
            ])
            
    print(f"[OK] Fetched {len(rows)} GSC queries & pages. Saved to: {output_file}")
    return rows

if __name__ == "__main__":
    fetch_gsc_queries()
