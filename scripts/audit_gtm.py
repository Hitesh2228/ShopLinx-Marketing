import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
key = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
creds = service_account.Credentials.from_service_account_file(
    key, scopes=["https://www.googleapis.com/auth/tagmanager.readonly"]
)

gtm = build("tagmanager", "v2", credentials=creds)

# Container path for ShopLinx (Account: 6320815998)
# Let's find workspace in container
containers = gtm.accounts().containers().list(parent="accounts/6320815998").execute().get("container", [])
for c in containers:
    if c.get("name") == "ShopLinx":
        c_path = c.get("path")
        print(f"\n=== INSPECTING CONTAINER: {c.get('name')} ({c.get('publicId')}) ===")
        workspaces = gtm.accounts().containers().workspaces().list(parent=c_path).execute().get("workspace", [])
        if workspaces:
            w_path = workspaces[0].get("path")
            print(f"Workspace: {workspaces[0].get('name')}")
            
            # Tags
            tags = gtm.accounts().containers().workspaces().tags().list(parent=w_path).execute().get("tag", [])
            print(f"\n--- Tags ({len(tags)}) ---")
            for t in tags:
                print(f"  * [{t.get('type')}] {t.get('name')}")
                
            # Triggers
            triggers = gtm.accounts().containers().workspaces().triggers().list(parent=w_path).execute().get("trigger", [])
            print(f"\n--- Triggers ({len(triggers)}) ---")
            for tr in triggers:
                print(f"  * [{tr.get('type')}] {tr.get('name')}")
