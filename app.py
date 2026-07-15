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

    return {
        "success": True,
        "file_id": file_id
    }
