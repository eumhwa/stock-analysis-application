import json
from pydantic import BaseSettings

class Config(BaseSettings):
    
    code_json_path:str = "./stock_code.json"
    stock_code = json.load(self.code_json_path)

    base_price_url:str = "https://finance.naver.com/item/sise.naver?code="

if __name__ == "__main__":
    config = Config()