import json
from pydantic import BaseSettings

class Config(BaseSettings):
    '''
    headers -> http://www.useragentstring.com/
    '''

    code_json_path:str = "./fastapi_app/stock_code.json"
    stock_code:dict = {}
    bs4_parser:str = "html.parser"

    base_stock_price_url:str = "https://finance.naver.com/item/sise_day.naver?code="
    headers:dict = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"}
    price_data_cols:list = ["date", "last_price", "diff", "start_price", "high_price", "low_price", "volume"]
    not_use_col:list = ["diff"]
    max_page:int = 500
    
    frontend_url:str = "http://localhost:8000"
    algorithm_url:str = ""

def load_code_json(json_path:str):
    with open(json_path, "r", encoding="UTF-8") as f:
        json_data = json.load(f)

    return json_data


config = Config()
config.stock_code = load_code_json(config.code_json_path)
