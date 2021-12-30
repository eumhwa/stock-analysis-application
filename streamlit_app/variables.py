import json
from pydantic import BaseSettings

class Config(BaseSettings):

    code_json_path:str = "./fastapi_app/stock_code.json"
    stock_code:dict = {}
    
    demo_stock_name:str = "삼성전자"
    demo_year:int = 2021
    demo_month:int = 1
    demo_day:int = 1
    demo_ndata:int = 200
    
    job_id:str = ""
    job_id_size:int = 7
    available_model_set:tuple = ('ARIMA', 'TFT', 'N-Beats')
    
    frontend_url:str = "http://172.26.0.3:8000"
    test_frontend_url:str = "http://172.26.0.3:8001"
    backend_url:str = "http://172.26.0.2:8002"
    test_backend_url:str = "http://172.26.0.2:8003"
    
    algorithm_url:str = ""

def load_code_json(json_path:str):
    with open(json_path, "r", encoding="UTF-8") as f:
        json_data = json.load(f)

    return json_data


config = Config()
config.stock_code = load_code_json(config.code_json_path)
