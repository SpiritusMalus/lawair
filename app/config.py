from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    FERNET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REDIS_URL: str = "redis://redis:6379/0"
    PROJECT_NAME: str = "lawair"

    ENVIRONMENT: str = "local"  # local | staging | production

    # SMTP — leave SMTP_HOST empty to disable sending (logs instead)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_TLS: bool = True  # True = SMTP_SSL (port 465); False = STARTTLS (port 587)

    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    FRONTEND_URL: str = "http://localhost:3000"
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
