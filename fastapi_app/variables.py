import os, json
from pydantic import BaseSettings

class Config(BaseSettings):
    '''
    headers -> http://www.useragentstring.com/
    '''

    code_json_path:str = "./fastapi_app/stock_code.json"
    data_path:str = "./data"
    stock_code:dict = {}
    bs4_parser:str = "html.parser"

    base_stock_price_url:str = "https://finance.naver.com/item/sise_day.naver?code="
    headers:dict = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
    price_data_cols:list = ["date", "last_price", "diff", "start_price", "high_price", "low_price", "volume"]
    not_use_col:list = ["diff"]
    
    n_cpu:int = os.environ["N_CPU"]

    frontend_url:str = f"{os.environ["FE_URL"]}:{os.environ["FE_PORT"]}"
    test_frontend_url:str = f"{os.environ["FE_URL"]}:{os.environ["FE_TEST_PORT"]}"
    backend_url:str = f"{os.environ["BE_URL"]}:{os.environ["BE_PORT"]}"
    test_backend_url:str = f"{os.environ["BE_URL"]}:{os.environ["BE_TEST_PORT"]}"
    
    algorithm_url:str = ""

def load_code_json(json_path:str):
    with open(json_path, "r", encoding="UTF-8") as f:
        json_data = json.load(f)

    return json_data


config = Config()
config.stock_code = load_code_json(config.code_json_path)
