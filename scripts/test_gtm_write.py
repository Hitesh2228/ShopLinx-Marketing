import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds = service_account.Credentials.from_service_account_file(
    key, scopes=["https://www.googleapis.com/auth/tagmanager.edit.containers"]
)

gtm = build("tagmanager", "v2", credentials=creds)

try:
    # Get container and workspaces
    containers = gtm.accounts().containers().list(parent="accounts/6320815998").execute().get("container", [])
    for c in containers:
        if c.get("name") == "ShopLinx":
            w_list = gtm.accounts().containers().workspaces().list(parent=c.get("path")).execute().get("workspace", [])
            if w_list:
                w_path = w_list[0].get("path")
                print(f"Container: {c.get('name')}, Workspace: {w_list[0].get('name')}")
                
                # Try creating a dummy test trigger or variable, or inspect permission
                # Let's test creating a draft variable or checking authorization
                print("[INFO] Attempting to test write access...")
                test_var = {
                    "name": "_test_permission_check",
                    "type": "c",
                    "parameter": [{"type": "template", "key": "value", "value": "test"}]
                }
                res = gtm.accounts().containers().workspaces().variables().create(parent=w_path, body=test_var).execute()
                print(f"[SUCCESS] Write permission is ACTIVE! Created test variable ID: {res.get('variableId')}")
                
                # Immediately clean it up so we leave no traces
                gtm.accounts().containers().workspaces().variables().delete(path=res.get("path")).execute()
                print("[SUCCESS] Test variable cleaned up successfully. GTM is fully writable!")
except Exception as e:
    print(f"[RESULT] {e}")
