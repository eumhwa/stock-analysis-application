import os
import json
import requests

from fastapi import APIRouter, Response, status, HTTPException

from ..variables import config

router = APIRouter()


@router.post(
    "/sample-api",
    summary="[predict-001] 기능",
    description="",
    # response_model=str,
)
def function():
    return
