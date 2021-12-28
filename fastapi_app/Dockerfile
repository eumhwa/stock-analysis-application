FROM python:3.8

WORKDIR /code/
COPY . /code/

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN apt-get update && apt-get install -y vim


CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8002"]
EXPOSE 8002

