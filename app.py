from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Google Drive Audio Service is running"
    }
