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
@app.post("/test")
def test():
    return {
        "success": True,
        "message": "Endpoint works"
    }
