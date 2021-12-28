cd ../fastapi_app && docker build -t backend:dev .
# docker run -itd -p 8002:8002 --name backend backend:dev

cd ../streamlit_app && docker build -t frontend:dev .
# docker run -itd -p 8000:8000 --name frontend frontend:dev