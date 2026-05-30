from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openweather_api_key: str = ""
    ticketmaster_api_key: str = ""
    geoapify_api_key: str = ""
    news_api_key: str = ""
    email_user: str = ""
    email_pass: str = ""
    llm_api_key: str = ""
    llm_model: str = "mistral"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
