#syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

RUN pip install seaborn pandas jupyter scikit-learn

COPY . .

CMD ["jupyter", "notebook",  "--no-browser", "--port=8888", "--ip=0.0.0.0", "--allow-root"]
