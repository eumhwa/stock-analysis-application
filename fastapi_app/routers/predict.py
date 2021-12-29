import os
import json
import requests

from fastapi import APIRouter, Response, status, HTTPException

from ..variables import config

router = APIRouter()


@router.post(
    "/start-forecast",
    summary="[predict-001] forecasting api",
    description="",
    # response_model=str,
)
def start_forecasting():
    return
