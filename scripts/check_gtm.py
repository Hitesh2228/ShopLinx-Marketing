import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds = service_account.Credentials.from_service_account_file(
    key, scopes=["https://www.googleapis.com/auth/tagmanager.readonly"]
)

try:
    gtm = build("tagmanager", "v2", credentials=creds)
    accounts = gtm.accounts().list().execute()
    account_list = accounts.get("account", [])
    if not account_list:
        print("[INFO] No GTM accounts found for this service account.")
    else:
        print(f"[SUCCESS] Found {len(account_list)} GTM account(s):")
        for a in account_list:
            acc_id = a.get("accountId")
            acc_name = a.get("name")
            print(f"  - Account: {acc_name} (ID: {acc_id})")
            containers = gtm.accounts().containers().list(parent=a.get("path")).execute()
            for c in containers.get("container", []):
                print(f"    * Container: {c.get('name')} (GTM Public ID: {c.get('publicId')})")
except Exception as e:
    print(f"[FAIL] GTM Error: {e}")
