pytest:
	python -m pytest


restart:
	docker compose down
	docker compose up -d

