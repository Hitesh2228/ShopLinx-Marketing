import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
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
    c_name = c.get("name")
    c_id = c.get("publicId")
    print(f"\n{'='*65}")
    print(f" CONTAINER: {c_name} ({c_id})")
    print(f"{'='*65}")
    w_list = gtm.accounts().containers().workspaces().list(parent=c.get("path")).execute().get("workspace", [])
    if w_list:
        w_path = w_list[0].get("path")
        tags = gtm.accounts().containers().workspaces().tags().list(parent=w_path).execute().get("tag", [])
        triggers = gtm.accounts().containers().workspaces().triggers().list(parent=w_path).execute().get("trigger", [])
        variables = gtm.accounts().containers().workspaces().variables().list(parent=w_path).execute().get("variable", [])
        
        print(f"Total Tags     : {len(tags)}")
        print(f"Total Triggers : {len(triggers)}")
        print(f"Total Variables: {len(variables)}")
        
        print("\n--- TAGS ---")
        for t in tags:
            print(f"  * [{t.get('type'):<10}] {t.get('name')}")
            
        print("\n--- TRIGGERS ---")
        for tr in triggers:
            print(f"  * [{tr.get('type'):<15}] {tr.get('name')}")
            
        print("\n--- VARIABLES ---")
        for v in variables:
            print(f"  * [{v.get('type'):<10}] {v.get('name')}")
