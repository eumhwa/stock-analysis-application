import os
import uvicorn

from fastapi import FastAPI, Response, status
from fastapi.testclient import TestClient

from .routers import crawl, train, predict
from .variables import config

def create_app() -> FastAPI:
    return FastAPI(title="Stock-Analysis Backend API server")

app = create_app()
# client = TestClient(app)

app.include_router(
    crawl.router, prefix=f"/crawl", tags=["Crawling"]
)
app.include_router(
    train.router, prefix=f"/train", tags=["Train"]
)
app.include_router(
    predict.router, prefix=f"/predict", tags=["Forecast"]
)