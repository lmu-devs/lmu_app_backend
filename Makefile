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
	docker compose exec api_v1 alembic revision --autogenerate -m "auto"

alembic-upgrade:
	docker compose exec api_v1 alembic upgrade head

alembic-downgrade:
	docker compose exec api_v1 alembic downgrade
