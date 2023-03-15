FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
COPY . /code/