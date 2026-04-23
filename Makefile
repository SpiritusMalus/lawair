.PHONY: up down build restart logs logs-web logs-db migrate migration shell ps

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart web

logs:
	docker compose logs -f

logs-web:
	docker compose logs -f web

logs-db:
	docker compose logs -f db

ps:
	docker compose ps

migrate:
	docker compose exec web alembic upgrade head

migration:
	@read -p "Migration name: " name; \
	docker compose exec web alembic revision --autogenerate -m "$$name"

shell:
	docker compose exec web bash
