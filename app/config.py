"""
Application configuration - loaded from environment variables / .env file
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App identity
    app_name: str = "EAS Tire & Auto AI Receptionist"
    business_name: str = "EAS Tire & Auto"
    receptionist_name: str = "Makayla"

    # Public base URL Twilio will POST to
    base_url: str = "http://localhost:8000"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    # Anthropic / Claude
    anthropic_api_key: str = ""

    # Business details spoken by Makayla
    business_phone: str = "(555) 123-4567"
    business_address: str = "123 Auto Drive, City, State 12345"
    business_hours: str = (
        "Monday through Friday 8 AM to 6 PM, Saturday 8 AM to 4 PM"
    )


settings = Settings()
