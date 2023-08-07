FROM python:3.10-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /service

RUN mkdir /service/static && mkdir /service/media

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt