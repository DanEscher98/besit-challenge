from fastapi import FastAPI
from datetime import datetime

app = FastAPI()


@app.get("/", summary="Root API status endpoint")
def home():
    return {
        "message": "Phinder challenge API",
        "version": "0.0.1",
        "timestamp": datetime.now().isoformat(),
    }
