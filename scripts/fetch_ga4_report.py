import os
import csv
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension

load_dotenv()

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "488623822")

def fetch_ga4_traffic(date_range="30daysAgo"):
    creds = service_account.Credentials.from_service_account_file(KEY_FILE)
    client = BetaAnalyticsDataClient(credentials=creds)

    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionDefaultChannelGroup"),
            Dimension(name="sessionSourceMedium")
        ],
        metrics=[
            Metric(name="activeUsers"),
            Metric(name="sessions"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date=date_range, end_date="today")],
    )

    response = client.run_report(request)
    os.makedirs("data/processed", exist_ok=True)
    output_file = "data/processed/ga4_traffic_channels.csv"

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Channel Group", "Source / Medium", "Active Users", "Sessions", "Bounce Rate (%)", "Avg Duration (sec)"])
        for row in response.rows:
            channel = row.dimension_values[0].value
            source_medium = row.dimension_values[1].value
            active_users = row.metric_values[0].value
            sessions = row.metric_values[1].value
            bounce_rate = f"{float(row.metric_values[2].value) * 100:.2f}"
            duration = f"{float(row.metric_values[3].value):.1f}"
            writer.writerow([channel, source_medium, active_users, sessions, bounce_rate, duration])

    print(f"[OK] Fetched {len(response.rows)} GA4 traffic channels. Saved to: {output_file}")

if __name__ == "__main__":
    fetch_ga4_traffic()
