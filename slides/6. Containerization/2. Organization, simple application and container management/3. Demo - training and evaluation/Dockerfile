#syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3","run.py"]