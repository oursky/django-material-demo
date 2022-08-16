# syntax=docker/dockerfile:1

FROM python:3

WORKDIR /django_material_demo

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY /django_material_demo .

RUN python manage.py migrate
RUN DJANGO_SUPERUSER_PASSWORD=demo python manage.py createsuperuser --noinput --username demo --email demo@mail.com
RUN python manage.py loaddata polls/sample_data.json

EXPOSE 8000
CMD make runserver
