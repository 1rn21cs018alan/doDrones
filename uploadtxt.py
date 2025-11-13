import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.appdata",
          "https://www.googleapis.com/auth/drive.file"]


def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        raise FileNotFoundError("No Token File")

    try:
        media = MediaFileUpload("testData.txt")
        metadata={
            "name":"try/test.txt"
        }
        service = build("drive", "v3", credentials=creds)
        result=(
            service.files()
            .create(body=metadata,media_body=media,fields="id")
            .execute()
        )
        print(f'File ID: {result.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
