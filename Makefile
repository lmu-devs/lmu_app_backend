setup:
	docker network create shared
	docker compose up api_dev data_fetcher_dev

pytest:
	python -m pytest

restart:
	docker compose restart

build:
	sudo docker compose build

run:
	sudo docker compose up

up:
	docker compose up


alembic-auto:
	docker compose exec api_dev alembic revision --autogenerate -m "auto"

alembic-upgrade:
	docker compose exec api_dev alembic upgrade head

alembic-downgrade:
	docker compose exec api_dev alembic downgrade
