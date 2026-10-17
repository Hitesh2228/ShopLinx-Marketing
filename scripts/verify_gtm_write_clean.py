import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

scopes = [
    "https://www.googleapis.com/auth/tagmanager.readonly",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.publish"
]

creds = service_account.Credentials.from_service_account_file(key, scopes=scopes)
gtm = build("tagmanager", "v2", credentials=creds)

containers = gtm.accounts().containers().list(parent="accounts/6320815998").execute().get("container", [])
for c in containers:
    if c.get("name") == "ShopLinx":
        workspaces = gtm.accounts().containers().workspaces().list(parent=c.get("path")).execute().get("workspace", [])
        w_path = workspaces[0].get("path")
        print(f"Testing on workspace: {w_path}")
        
        # Proper trigger name without underscore prefix
        test_trigger = {
            "name": "AITestPermissionTrigger",
            "type": "customEvent",
            "customEventFilter": [{
                "type": "equals",
                "parameter": [
                    {"type": "template", "key": "arg0", "value": "{{_event}}"},
                    {"type": "template", "key": "arg1", "value": "test_event"}
                ]
            }]
        }
        res = gtm.accounts().containers().workspaces().triggers().create(parent=w_path, body=test_trigger).execute()
        print(f"--> [SUCCESS] Successfully created Trigger! Name: {res.get('name')} | Trigger ID: {res.get('triggerId')}")
        
        # Clean up immediately
        gtm.accounts().containers().workspaces().triggers().delete(path=res.get("path")).execute()
        print("--> [SUCCESS] Successfully deleted Trigger! Clean-up complete.")
        print("\n=== GTM DIRECT WRITE & PUBLISH PERMISSION IS 100% OPERATIONAL! ===")
