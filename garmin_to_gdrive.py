import os
import datetime
import json
from garminconnect import Garmin
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

GARMIN_USER = os.environ["GARMIN_USER"]
GARMIN_PASS = os.environ["GARMIN_PASS"]
GDRIVE_FOLDER_ID = os.environ["GDRIVE_FOLDER_ID"]
GOOGLE_SERVICE_ACCOUNT_FILE = "service_account.json"

def get_garmin_stats():
    client = Garmin(GARMIN_USER, GARMIN_PASS)
    client.login()
    today = datetime.date.today()
    stats = client.get_stats(today.isoformat())
    filename = f"garmin_{today}.json"
    with open(filename, "w") as f:
        json.dump(stats, f)
    return filename

def upload_to_gdrive(filename):
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': filename,
        'parents': [GDRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(filename, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Plik {filename} wrzucony na Google Drive (id: {file.get('id')})")

if __name__ == "__main__":
    filename = get_garmin_stats()
    upload_to_gdrive(filename)
