from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: str = "development"
    secret_key: str
    frontend_url: str = "http://localhost:3000"
    use_mocks: bool = False

    # Database
    database_url: str

    # Microsoft Graph
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # Google APIs
    google_vision_api_key: str = ""
    google_maps_api_key: str = ""
    google_stt_api_key: str = ""

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemini-2.5-flash"

    # Railway Object Storage (S3-compatible)
    storage_access_key: str = ""
    storage_secret_key: str = ""
    storage_bucket: str = ""
    storage_endpoint: str = ""

    # Meeting defaults
    meeting_duration_minutes: int = 60


def get_settings() -> Settings:
    return Settings()
