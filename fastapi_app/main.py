import os
import uvicorn

from fastapi import FastAPI, Response, status
from fastapi.testclient import TestClient

from routers import crawl
from variables import config

def create_app() -> FastAPI:
    return FastAPI(title="Stock analysis backend API server")

app = create_app()
client = TestClient(app)

app.include_router(
    crawl.router, prefix=f"/crawl", tags=["Crawling"]
)