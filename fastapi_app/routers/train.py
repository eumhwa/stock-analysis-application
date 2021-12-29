import os
import json
import requests

from fastapi import APIRouter, Response, status, HTTPException

from ..variables import config
from .crawl import scrap_price, validate_date

router = APIRouter()

@router.post(
    "/start-training",
    summary="[training-001] training api",
    description="",
    # response_model=str,
)
def start_training(
    stock_name:str, start_year:int=2020, start_month:int=1, start_day:int=1, valid_rate:float=0.9
    ):
    if validate_date(start_year, start_month, start_day):
        raise HTTPException(status_code=400, detail="date format error")

    data = scrap_price(stock_name, start_year, start_month, start_day)

    return
