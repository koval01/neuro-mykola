from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    BOT_API_KEY: str
    WORK_CHAT_ID: int

    class Config:
        env_file = "./.env.local"


settings = Settings()
