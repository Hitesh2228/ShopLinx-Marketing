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

try:
    perms = gtm.accounts().user_permissions().list(parent="accounts/6320815998").execute()
    for u in perms.get("userPermission", []):
        email = u.get("emailAddress")
        acc_perm = u.get("accountAccess", {}).get("permission")
        container_perms = u.get("containerAccess", [])
        print(f"User: {email} | Account: {acc_perm}")
        for cp in container_perms:
            print(f"   -> Container: {cp.get('containerId')} | Permission: {cp.get('permission')}")
except Exception as e:
    print("Error:", e)
