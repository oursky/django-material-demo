# Put GENERATE_SECRET into files you want to generate secret
# Usage: `make generate-secret FROM=/path/to/src TO=/path/to/dest`
.PHONY: generate-secret
generate-secret:
	curl -s https://raw.githubusercontent.com/oursky/devsecops-secret/v1.0/generate-secret.sh \
		| bash -s -- ${FROM} ${TO}

.PHONY: secret
secret:
	make generate-secret FROM=.env.example TO=.env

.PHONY: setup
setup: secret
	docker compose up --build --no-start
	make migrations
	make migrate
	make load-data
	
.PHONY: start
start:
	docker compose up

.PHONY: clean
clean:
	docker compose down

.PHONY: migrations
migrations:
	docker compose run --rm web python manage.py makemigrations

.PHONY: migrate
migrate:
	docker compose run --rm web python manage.py migrate

.PHONY: load-data
load-data:
	docker compose run --rm web python manage.py loaddata polls/sample_data.json

.PHONY: create-superuser
create-superuser:
	docker compose run --rm web python manage.py createsuperuser
