FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements_net.txt requirements_net.txt

RUN pip install --upgrade pip
RUN pip install -r requirements_net.txt

COPY mysite .