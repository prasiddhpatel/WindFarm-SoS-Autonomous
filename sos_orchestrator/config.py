from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://sos:sos_password@localhost:5432/windfarm_sos"
    telemetry_url: str = "postgresql+psycopg://telemetry:telemetry_password@localhost:5433/telemetry"
    redis_url: str = "redis://localhost:6379/0"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic_prefix: str = "fleet"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
