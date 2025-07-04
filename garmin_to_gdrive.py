import os
import datetime
import json
from garminconnect import Garmin
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Dane logowania do Garmina (zdefiniujesz jako sekrety w GitHub)
GARMIN_USER = os.environ["GARMIN_USER"]
GARMIN_PASS = os.environ["GARMIN_PASS"]

# Google Drive - nazwa folderu docelowego (możesz zmienić)
GDRIVE_FOLDER_NAME = "Garmin"

# Plik credentials do Service Account
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

    # Sprawdź czy folder istnieje, jeśli nie – utwórz
    folder_id = None
    results = service.files().list(
        q=f"name='{GDRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields='files(id, name)').execute()
    items = results.get('files', [])
    if items:
        folder_id = items[0]['id']
    else:
        file_metadata = {
            'name': GDRIVE_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')

    # Upload pliku
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    media = MediaFileUpload(filename, mimetype='application/json')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Plik {filename} wrzucony na Google Drive (id: {file.get('id')})")

if __name__ == "__main__":
    filename = get_garmin_stats()
    upload_to_gdrive(filename)
