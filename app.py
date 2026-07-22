from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import json
import re
import subprocess
import io
from pydantic import BaseModel

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = FastAPI()

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

    credentials_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
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

   ffmpeg_version = subprocess.run(
    ["ffmpeg", "-version"],
    capture_output=True,
    text=True
)

return {
    "success": True,
    "video_exists": os.path.exists(video_path),
    "video_size": os.path.getsize(video_path),
    "ffmpeg_installed": ffmpeg_version.returncode == 0,
    "ffmpeg_output": ffmpeg_version.stdout.split("\n")[0]
}
