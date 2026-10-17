import os
import sys
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "488623822")

def audit_running_paid_ads(days=30):
    """
    Fetches real-time live performance of all paid Google Ads and Meta Ads campaigns.
    Analyzes User Engagement, Bounce Rates, Drop-offs, and Actual Signups.
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
                Dimension(name="sessionCampaignName"),
                Dimension(name="sessionSourceMedium")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="averageSessionDuration"),
                Metric(name="bounceRate"),
                Metric(name="keyEvents:ads_conversion_SIGNUP_1")
            ],
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        )

        res = client.run_report(req)
        print("=" * 70)
        print("   LIVE PAID ADS PERFORMANCE & AUDIT REPORT")
        print("=" * 70)

        paid_found = False
        for row in res.rows:
            camp = row.dimension_values[0].value
            src = row.dimension_values[1].value
            if any(k in src.lower() for k in ["cpc", "paid", "meta", "facebook", "instagram"]) or "ad" in camp.lower():
                paid_found = True
                sess = row.metric_values[0].value
                users = row.metric_values[1].value
                dur = float(row.metric_values[2].value)
                bounce = float(row.metric_values[3].value) * 100
                signups = row.metric_values[4].value

                # Diagnosis
                status = "🏆 WINNER (Low Bounce, High Engagement)" if bounce < 20 else "⚠️ OPTIMIZE (High Bounce Rate)" if bounce > 40 else "✅ STABLE"

                print(f"\n[CAMPAIGN] {camp}")
                print(f"  Source/Medium : {src}")
                print(f"  Traffic       : {sess} Sessions | {users} Active Users")
                print(f"  Engagement    : Avg Time: {dur:.1f}s | Bounce Rate: {bounce:.1f}%")
                print(f"  Conversions   : {signups} Signups Recorded")
                print(f"  Diagnosis     : {status}")

        if not paid_found:
            print("\n[INFO] No active paid ads detected in the selected date range.")

        print("\n" + "=" * 70)
    except Exception as e:
        print(f"[ERROR] Could not fetch paid ads data: {e}")

if __name__ == "__main__":
    audit_running_paid_ads(days=60)
