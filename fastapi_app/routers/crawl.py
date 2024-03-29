import os, time
import json
import string
import random
import requests
import pandas as pd

from datetime import datetime
from urllib import request, parse
from bs4 import BeautifulSoup
from fastapi import APIRouter, Response, status, HTTPException

from ..variables import config, load_code_json
import ray

router = APIRouter()
ray.init(num_cpus=config.n_cpu, ignore_reinit_error=True)

# udf
def validate_date(y:int, m:int, d:int) -> bool:
    error = False
    try:
        date = datetime.strptime(f"{y}.{m}.{d}", "%Y.%m.%d")
        if date > datetime.now(): error = True
        if y <= 2017: error = True # support after 2018
    except:
        error = True
    
    return  error

@ray.remote
def crawl_price(req_url:str):
    res = requests.get(req_url, headers=config.headers)
    return pd.read_html(res.text, encoding="euc-kr")[0]
    
def merge_data(data:pd.DataFrame, unit_df:pd.DataFrame):
    return pd.concat([data, unit_df], ignore_index=True)


@router.get(
    "/scrap-price",
    summary="[crawling-001] stock price data crawling api",
    description="",
    # response_model=str,
)
def scrap_price(stock_name:str, start_year:int=2020, start_month:int=1, start_day:int=1):
    if validate_date(start_year, start_month, start_day):
        raise HTTPException(status_code=400, detail="date format error")
    
    config.stock_code = load_code_json(config.code_json_path)
    try:
        stock_code = config.stock_code[stock_name]
        print(f"#1. stock name and code matched - {stock_name}:{stock_code}")
    except:
        raise HTTPException(status_code=400, detail="given stock name doesn't exist in json file update json first")
        print("[Error] Exception occured")
    
    stock_url = f"{config.base_stock_price_url}{stock_code}"
    res = requests.get(stock_url, headers=config.headers)
    
    soup = BeautifulSoup(res.text, config.bs4_parser)
    last_page = int(soup.find("td", class_='pgRR').a["href"].split("=")[-1])
    print(f"#2. last page number is {last_page}")
    
    tic = time.time()
    start_date = datetime.strptime(f"{start_year}.{start_month}.{start_day}", "%Y.%m.%d")
    data = None
    for p in range(1, last_page+1):
        res = requests.get(f"{stock_url}&page={p}", headers=config.headers)
        tmp = pd.read_html(res.text, encoding="euc-kr")[0]
        data = pd.concat([data, tmp], ignore_index=True)

        tmp_min_date = pd.to_datetime(tmp.iloc[:, 0]).min(skipna=True)
        if tmp_min_date <= start_date:
            print("#3. iteration breaked!")
            break
    
    print(f"#4. duration: {time.time() - tic}")
    data.dropna(inplace=True)
    data.reset_index(drop=True)
    
    data.columns = config.price_data_cols
    data = data.drop(config.not_use_col, axis=1)
    data = data.sort_values(by="date", ascending=True)
    data["date"] = pd.to_datetime(data["date"])
    data = data.loc[data["date"] >= start_date, :].reset_index(drop=True)
    
    print(data.head())
    print(f"#5. crawled data shape is {data.shape}")
    return  data.to_json()


@router.get(
    "/scrap-price-ray",
    summary="[crawling-002] stock price data crawling api using ray",
    description="",
    # response_model=str,
)
def scrap_price(stock_name:str, start_year:int=2020, start_month:int=1, start_day:int=1):
    if validate_date(start_year, start_month, start_day):
        raise HTTPException(status_code=400, detail="date format error")
    
    config.stock_code = load_code_json(config.code_json_path)
    try:
        stock_code = config.stock_code[stock_name]
        print(f"#1. stock name and code matched - {stock_name}:{stock_code}")
    except:
        raise HTTPException(status_code=400, detail="given stock name doesn't exist in json file update json first")
        print("[Error] Exception occured")
    
    stock_url = f"{config.base_stock_price_url}{stock_code}"
    res = requests.get(stock_url, headers=config.headers)
    
    soup = BeautifulSoup(res.text, config.bs4_parser)
    last_page = int(soup.find("td", class_='pgRR').a["href"].split("=")[-1])
    print(f"#2. last page number is {last_page}")
    
    tic = time.time()
    start_date = datetime.strptime(f"{start_year}.{start_month}.{start_day}", "%Y.%m.%d")
    res = requests.get(f"{stock_url}&page={1}", headers=config.headers)
    data = pd.read_html(res.text, encoding="euc-kr")[0]
    jobs = [crawl_price.remote(f"{stock_url}&page={p}") for p in range(2, last_page+1)]

    for _ in range(len(jobs)):
        done, jobs = ray.wait(jobs)
        tmp = ray.get(done[0])
        data = merge_data(data, tmp)

        tmp_min_date = pd.to_datetime(tmp.iloc[:, 0]).min(skipna=True)
        if tmp_min_date <= start_date:
            print("#3. iteration breaked!")
            break
    
    print(f"#4. duration: {time.time() - tic}")
    data.dropna(inplace=True)
    data.reset_index(drop=True)
    
    data.columns = config.price_data_cols
    data = data.drop(config.not_use_col, axis=1)
    data = data.sort_values(by="date", ascending=True)
    data["date"] = pd.to_datetime(data["date"])
    data = data.loc[data["date"] >= start_date, :].reset_index(drop=True)
    
    print(data.head())
    print(f"#5. crawled data shape is {data.shape}")
    return  data.to_json()

@router.put(
    "/update_code",
    summary="[crawling-003] stock code json updating API",
    description="",
    # response_model=str,
    )
def update_stock_code(stock_name:str, stock_code:str):
	
    try:
        code_dict = load_code_json(config.code_json_path)
    except:
        raise HTTPException(status_code=500, detail="json not found")      

    code_dict[stock_name] = stock_code
    with open(config.code_json_path, "w", encoding="UTF-8") as o:
        json.dump(code_dict, o, ensure_ascii = False)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/id",
    summary="[crawling-004] job id API",
    description="",
    # response_model=str,
    )
def create_job_id(size:int=7):
    chars = ','.join(string.ascii_lowercase).split(',')
    numbers = list(map(str, list(range(10))))
    cand = chars + numbers
    return ''.join(random.sample(cand, size))