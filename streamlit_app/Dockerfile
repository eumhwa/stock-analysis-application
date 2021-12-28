FROM python:3.8

WORKDIR /code/
COPY . /code/

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
# RUN apt-get update && apt-get install -y vim


CMD ["streamlit", "run", "./streamlit_app/main.py"]
EXPOSE 8501

