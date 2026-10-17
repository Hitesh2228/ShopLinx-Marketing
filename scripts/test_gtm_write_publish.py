import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Try with publish scope
creds = service_account.Credentials.from_service_account_file(
    key, scopes=["https://www.googleapis.com/auth/tagmanager.publish"]
)
gtm = build("tagmanager", "v2", credentials=creds)

try:
    containers = gtm.accounts().containers().list(parent="accounts/6320815998").execute().get("container", [])
    for c in containers:
        if c.get("name") == "ShopLinx":
            workspaces = gtm.accounts().containers().workspaces().list(parent=c.get("path")).execute().get("workspace", [])
            w_path = workspaces[0].get("path")
            print(f"Testing on workspace: {w_path}")
            
            # Let's try creating a dummy trigger
            test_trigger = {
                "name": "_permission_test_trigger",
                "type": "customEvent",
                "customEventFilter": [{
                    "type": "equals",
                    "parameter": [
                        {"type": "template", "key": "arg0", "value": "{{_event}}"},
                        {"type": "template", "key": "arg1", "value": "_test_event"}
                    ]
                }]
            }
            res = gtm.accounts().containers().workspaces().triggers().create(parent=w_path, body=test_trigger).execute()
            print(f"--> [SUCCESS] Successfully created trigger! Trigger ID: {res.get('triggerId')}")
            
            # Clean up
            gtm.accounts().containers().workspaces().triggers().delete(path=res.get("path")).execute()
            print("--> [SUCCESS] Successfully deleted trigger. Write/Edit access is 100% WORKING!")
except Exception as e:
    print(f"--> [ERROR] {e}")
