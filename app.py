from fastapi import FastAPI, HTTPException
import os
import json
import re
import subprocess
import io
import requests

from pydantic import BaseModel

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = FastAPI()

AUDIO_FOLDER_ID = "13-kBZvyZYTFK_2xw1bkMIMa-pfsQN_pu"

class DriveRequest(BaseModel):
    url: str


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Google Drive Audio Service is running"
    }


@app.post("/test")
def test():
    return {
        "success": True,
        "message": "Endpoint works"
    }


@app.post("/drive")
def drive(request: DriveRequest):

    match = re.search(r"/d/([a-zA-Z0-9_-]+)", request.url)

    if not match:
        raise HTTPException(status_code=400, detail="Invalid Google Drive link")

    file_id = match.group(1)

    credentials_info = json.loads(
        os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
    )

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=credentials)

    file = service.files().get(
        fileId=file_id,
        fields="id,name,mimeType,size",
        supportsAllDrives=True
    ).execute()

    request_download = service.files().get_media(fileId=file_id)

    os.makedirs("temp", exist_ok=True)

    video_path = f"temp/{file_id}.mp4"

    with io.FileIO(video_path, "wb") as fh:
        downloader = MediaIoBaseDownload(fh, request_download)

        done = False

        while not done:
            status, done = downloader.next_chunk()

    audio_path = f"temp/{file_id}.mp3"

    subprocess.run(
        [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-y",
            audio_path
        ],
        check=True
    )

    api_key = os.environ["ASSEMBLYAI_API_KEY"]

    headers = {
        "authorization": api_key
    }

    with open(audio_path, "rb") as f:

        upload = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=f
        )

    upload.raise_for_status()

    upload_url = upload.json()["upload_url"]

    if os.path.exists(video_path):
        os.remove(video_path)

    if os.path.exists(audio_path):
        os.remove(audio_path)

    return {
        "success": True,
        "upload_url": upload_url,
        "file_name": file["name"]
    }
