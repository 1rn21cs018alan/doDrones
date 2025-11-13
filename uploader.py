import os.path
import os
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
import io

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.appdata",
          "https://www.googleapis.com/auth/drive.file"]

def upload(filename:str,fileData:bytes):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        raise FileNotFoundError("No Token File")

    try:
        f = io.BytesIO(fileData)
        media=MediaIoBaseUpload(f, mimetype='application/msword')
        metadata={
            "name":filename
        }
        service = build("drive", "v3", credentials=creds)
        result=(
            service.files()
            .create(body=metadata,media_body=media,fields="id")
            .execute()
        )
        
        return result.get("id")

    except HttpError as error:
        print(f"An error occurred: {error}")
        raise error


if __name__=="__main__":
    with open("testData.txt","rb") as f:
        print(upload("temp.py",f.read()))