# syntax=docker/dockerfile:1

FROM python:3-slim

RUN apt update -y && apt install -y build-essential libpq-dev
RUN apt install -y git

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR django_material_demo

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
