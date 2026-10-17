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

containers = gtm.accounts().containers().list(parent="accounts/6320815998").execute().get("container", [])
for c in containers:
    if c.get("name") == "ShopLinx":
        workspaces = gtm.accounts().containers().workspaces().list(parent=c.get("path")).execute().get("workspace", [])
        w_path = workspaces[0].get("path")
        tags = gtm.accounts().containers().workspaces().tags().list(parent=w_path).execute().get("tag", [])
        for t in tags:
            name = t.get("name")
            if "meta" in name.lower() or "pixel" in name.lower():
                print(f"Tag: {name}")
                for param in t.get("parameter", []):
                    if param.get("key") == "html":
                        for line in param.get("value", "").splitlines():
                            if "fbq(" in line or "init" in line:
                                print(f"   {line.strip()}")
