from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import json
import re
import subprocess
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

app = FastAPI()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Google Drive Audio Service is running"
    }


@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(temp_dir, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse({
        "success": True,
        "filename": filename,
        "path": filepath
    })
