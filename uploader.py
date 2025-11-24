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
import os
inSameFolder=lambda x:os.path.join(os.path.dirname(__file__),x) 
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.appdata",
          "https://www.googleapis.com/auth/drive.file"]

def upload(filename:str,fileData:bytes):
    creds = None
    tokenPath=inSameFolder('token.json')
    if os.path.exists(tokenPath):
        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
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