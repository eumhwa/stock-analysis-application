import os
import json
import requests
import pandas as pd

from urllib import request, parse
from bs4 import BeautifulSoup
from fastapi import APIRouter, Response, status, HTTPException

from ..variables import config, load_code_json

router = APIRouter()

@router.get(
    "/scrap",
    summary="[crawling-001] stock price data crawling api",
    description="",
    # response_model=str,
)
def function(stock_name:str):
    config.stock_code = load_code_json(config.code_json_path)
    try:
        stock_code = config.stock_code[stock_name]
        print(f"stock name and code matched - {stock_name}:{stock_code}")
    except:
        raise HTTPException(status_code=400, detail="given stock name doesn't exist in json file")
        print("exception occured")
    
    stock_url = f"{config.base_stock_price_url}{stock_code}"
    res = requests.get(stock_url, headers=config.headers)
    
    soup = BeautifulSoup(res.text, config.bs4_parser)
    last_page = min(int(soup.find("td", class_='pgRR').a["href"].split("=")[-1]), config.max_page)
    print(last_page)
    
    last_page=3
    data = None
    for p in range(1, last_page+1):
        res = requests.get(f"{stock_url}&page={p}", headers=config.headers)
        data = pd.concat([data, pd.read_html(res.text, encoding="euc-kr")[0]], ignore_index=True)
    data.dropna(inplace=True)
    data.reset_index(drop=True)
    data.columns = config.price_data_cols

    print(data.head(20))
    print(data.shape)
    return  data.to_json()


@router.put(
    "/update_code",
    summary="[crawling-002] stock code json updating API",
    description="",
    # response_model=str,
    )
def update_stock_code(stock_name:str, stock_code:str):
	
    try:
        code_dict = load_code_json(config.code_json_path)
    except:
        raise HTTPException(status_code=400, detail="json not found")      

    code_dict[stock_name] = stock_code
    with open(config.code_json_path, "w", encoding="UTF-8") as o:
        json.dump(code_dict, o, ensure_ascii = False)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
