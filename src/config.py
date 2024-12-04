from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """
    Configuration class for the application.
    """
    database_url: str
    download_path: str
