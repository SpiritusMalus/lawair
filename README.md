# lawair

Маркетплейс юридических услуг с AI-помощником по российскому праву.

## Что это

Платформа, где:

- **Клиент** задаёт вопрос AI, получает либо готовый ответ, либо шаблон документа, либо короткий список проверенных юристов под свою ситуацию
- **Юрист** регистрируется один раз, получает клиентов через AI-матчинг, работает через эскроу с прозрачной комиссией платформы
- **Продукт** не копирует Правовед: никаких фейковых «140+ юристов подобрано», никаких аукционов за клиента, никаких обязательных телефонов до оплаты

Подробнее о позиционировании и монетизации — в [CLAUDE.md](CLAUDE.md) и [COMPETITORS.md](COMPETITORS.md).

## Стек

- **Backend:** FastAPI + SQLAlchemy (async) + Alembic + PostgreSQL + Redis
- **AI:** RAG (LlamaIndex / LangChain) + GigaChat / Claude
- **Поиск:** pgvector (векторный) + Elasticsearch (полнотекстовый)
- **Файлы:** MinIO (S3-совместимый)
- **Фронт:** Next.js 14+ + TypeScript + Tailwind + shadcn/ui (отдельный репозиторий `lawair-frontend`)
- **Деплой:** Docker Compose, Yandex Cloud / Selectel (152-ФЗ)

## Запуск

```bash
cp .env.example .env          # заполнить значения
docker compose up -d --build
docker compose exec web alembic upgrade head
```

Swagger — [http://localhost:8000/docs](http://localhost:8000/docs).

Полный список команд — в [COMMANDS.md](COMMANDS.md).

## Документация

- [CLAUDE.md](CLAUDE.md) — архитектура, стек, бизнес-модель, решения по безопасности
- [COMPETITORS.md](COMPETITORS.md) — анализ рынка и стратегия
- [COMMANDS.md](COMMANDS.md) — команды, алиасы, Git Flow
