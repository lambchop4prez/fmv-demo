from pydantic_settings import BaseSettings


class MongoSettings(BaseSettings):
    HOST: str
    DATABASE: str
