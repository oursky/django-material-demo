# syntax=docker/dockerfile:1

FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR django_material_demo

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
