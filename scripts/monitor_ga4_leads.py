import os
import sys
import requests
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "488623822")

def check_community_conversions():
    """
    Checks GA4 for conversions and traffic originating from community channels.
    """
    try:
        from google.oauth2 import service_account
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

        creds = service_account.Credentials.from_service_account_file(KEY_FILE)
        client = BetaAnalyticsDataClient(credentials=creds)

        req = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            dimensions=[
                Dimension(name="sessionSourceMedium"),
                Dimension(name="sessionCampaignName")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="keyEvents:ads_conversion_SIGNUP_1")
            ],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        )

        res = client.run_report(req)
        print("=== GA4 CLOSED-LOOP ATTRIBUTION SCAN ===")
        for row in res.rows:
            source = row.dimension_values[0].value
            camp = row.dimension_values[1].value
            sessions = int(row.metric_values[0].value)
            signups = int(row.metric_values[1].value)

            if "reddit" in source.lower() or "quora" in source.lower() or "community" in camp.lower():
                print(f"🔥 Community Lead Detected: {source} | Sessions: {sessions} | Signups: {signups}")
                if signups > 0 and TOKEN and CHAT_ID:
                    alert_text = (
                        f"🎉 <b>COMMUNITY LEAD REVENUE ALERT!</b>\n\n"
                        f"📍 <b>Source:</b> {source}\n"
                        f"🎯 <b>Campaign:</b> {camp}\n"
                        f"👤 <b>New Signups:</b> {signups}\n\n"
                        f"<i>Your Reddit/Off-page answer successfully converted into a real user!</i>"
                    )
                    requests.post(API_URL, json={"chat_id": CHAT_ID, "text": alert_text, "parse_mode": "HTML"})
        print("Attribution scan complete.")
    except Exception as e:
        print(f"[GA4 Attribution Error] {e}")

if __name__ == "__main__":
    check_community_conversions()
