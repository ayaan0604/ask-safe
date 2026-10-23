
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Ask Safe"
    database_url: str
    gemini_api_key: str
    jwt_secret_key: str
    access_token_expire_minutes: int = 30
    allowed_origins : str
    supabase_url : str
    supabase_service_role_key : str
    supabase_bucket_name: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
