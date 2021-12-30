import os
import json
import requests

from datetime import datetime
from fastapi import APIRouter, Response, status, HTTPException
from pydantic import BaseModel

from ..variables import config
from .crawl import scrap_price, validate_date

router = APIRouter()

class TrainParameter(BaseModel):
    model_name:str = "TFT"
    valid_rate:float = 0.9
    input_window:int = 10
    output_window:int = 3

    class Config:
        orm_mode=True

class TrainInput(BaseModel):
    stock_name:str
    start_year:int = 2020
    start_month:int = 1
    start_day:int = 1
    train_parameter:TrainParameter

    class Config:
        orm_mode=True

@router.post(
    "/start-training",
    summary="[training-001] training api",
    description="",
    # response_model=str,
)
def start_training(inputs:TrainInput):
    if validate_date(inputs.start_year, inputs.start_month, inputs.start_day):
        raise HTTPException(status_code=400, detail="date format error")

    data = scrap_price(
        inputs.stock_name, inputs.start_year, inputs.start_month, inputs.start_day
        )

    print(inputs.train_parameter.__dict__)
    
    return
