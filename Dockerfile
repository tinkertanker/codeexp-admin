FROM python:3.9-slim

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install -r requirements.txt

COPY . /app

WORKDIR /app

ENTRYPOINT ["python3", "run.py"]