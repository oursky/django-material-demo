.PHONY: setup
setup:
	docker compose up --build --no-start
	
.PHONY: start
start:
	docker compose up

.PHONY: clean
clean:
	docker compose down

.PHONY: migrations
migrations:
	docker-compose run --rm web python manage.py makemigrations

.PHONY: migrate
migrate:
	docker-compose run --rm web python manage.py migrate

.PHONY: load-data
load-data:
	docker-compose run --rm web python manage.py loaddata polls/sample_data.json

.PHONY: create-superuser
create-superuser:
	docker-compose run --rm web python manage.py createsuperuser
