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
    job_id:str = "abcde"
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
    code_json = load_code_json(config.code_json_path)

    data = scrap_price(
        inputs.stock_name, inputs.start_year, inputs.start_month, inputs.start_day
        )

    input_dict = inputs.train_parameter.__dict__
    input_dict["job_id"] = inputs.job_id
    input_dict["stock_code"] = code_json[inputs.stock_name]
    print(input_dict)

    data_path = f"{config.data_path}/{input_dict['job_id']}"
    os.makedirs(data_path, exist_ok=True)
    with open(os.path.join(data_path, "data.json"), "w", encoding="UTF-8") as o:
        json.dump(data, o, ensure_ascii = False)
    
    with open(os.path.join(data_path, "status.json"), "w", encoding="UTF-8") as o:
        json.dump({"status":"running"}, o, ensure_ascii = False)

    with open(os.path.join(data_path, "config.json"), "w", encoding="UTF-8") as o:
        json.dump(input_dict, o, ensure_ascii = False)
    
    # docker api with job_id env

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/check-status",
    summary="[training-002] checking status api",
    description="",
    response_model=str,
)
def start_training(job_id:str):
    data_path = f"{config.data_path}/{job_id}"
    status_json_path = os.path.join(data_path, "status.json")

    try:
        with open(status_json_path, "r", encoding="UTF-8") as f:
            status = json.load(f)
    except:
        raise HTTPException(status_code=500, detail="status json not found")
    
    return status["status"]
