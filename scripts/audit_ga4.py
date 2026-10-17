import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
from google.analytics.admin import AnalyticsAdminServiceClient

load_dotenv()

KEY_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
PROPERTY_ID = os.getenv("GA4_PROPERTY_ID", "488623822")

creds = service_account.Credentials.from_service_account_file(KEY_FILE)
admin_client = AnalyticsAdminServiceClient(credentials=creds)
data_client = BetaAnalyticsDataClient(credentials=creds)

print("=" * 60)
print(f" GA4 DEEP AUDIT FOR PROPERTY: {PROPERTY_ID}")
print("=" * 60)

# 1. Google Ads Links
print("\n[1] Checking Google Ads Links in GA4:")
try:
    ads_links = admin_client.list_google_ads_links(parent=f"properties/{PROPERTY_ID}")
    count = 0
    for link in ads_links:
        count += 1
        print(f"  - Linked Ads Customer ID: {link.customer_id} (Can Manage: {link.can_manage_clients}, Creator: {link.creator_email_address})")
    if count == 0:
        print("  - [WARNING] No Google Ads account directly linked to GA4!")
except Exception as e:
    print(f"  - Error checking Google Ads links: {e}")

# 2. Key Events / Conversions list
print("\n[2] Checking Configured Key Events (Conversions):")
try:
    key_events = admin_client.list_key_events(parent=f"properties/{PROPERTY_ID}")
    ke_count = 0
    for ke in key_events:
        ke_count += 1
        print(f"  - Event: {ke.event_name} (Counting Method: {ke.counting_method})")
    if ke_count == 0:
        print("  - [WARNING] No Key Events (Conversions) marked in GA4!")
except Exception as e:
    print(f"  - Error checking Key Events: {e}")

# 3. All Event counts in last 30 days
print("\n[3] Top Events Triggered in last 30 days:")
try:
    req_events = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount"), Metric(name="totalUsers")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=20
    )
    res_events = data_client.run_report(req_events)
    for row in res_events.rows:
        print(f"  - {row.dimension_values[0].value:<25} | Count: {row.metric_values[0].value:<6} | Users: {row.metric_values[1].value}")
except Exception as e:
    print(f"  - Error fetching events: {e}")

# 4. Paid Traffic / Campaigns Performance
print("\n[4] Paid Campaigns / Source Performance in last 60 days:")
try:
    req_campaigns = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[
            Dimension(name="sessionSourceMedium"),
            Dimension(name="sessionCampaignName")
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date="60daysAgo", end_date="today")],
        limit=20
    )
    res_campaigns = data_client.run_report(req_campaigns)
    for row in res_campaigns.rows:
        src = row.dimension_values[0].value
        camp = row.dimension_values[1].value
        if "cpc" in src or "cpm" in src or "paid" in src.lower() or "google" in src:
            print(f"  - Source: {src:<20} | Campaign: {camp:<25} | Sess: {row.metric_values[0].value:<4} | Users: {row.metric_values[1].value:<4} | Bounce: {float(row.metric_values[2].value)*100:.1f}% | AvgDur: {float(row.metric_values[3].value):.1f}s")
except Exception as e:
    print(f"  - Error fetching campaign data: {e}")

# 5. Top Landing Pages
print("\n[5] Top 10 Landing Pages in last 30 days:")
try:
    req_pages = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name="landingPagePlusQueryString")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration")
        ],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=10
    )
    res_pages = data_client.run_report(req_pages)
    for row in res_pages.rows:
        page = row.dimension_values[0].value
        sess = row.metric_values[0].value
        users = row.metric_values[1].value
        bounce = f"{float(row.metric_values[2].value)*100:.1f}%"
        dur = f"{float(row.metric_values[3].value):.1f}s"
        print(f"  - {page:<45} | Sess: {sess:<4} | Users: {users:<4} | Bounce: {bounce:<6} | Dur: {dur}")
except Exception as e:
    print(f"  - Error fetching landing pages: {e}")
