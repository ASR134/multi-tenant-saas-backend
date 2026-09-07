from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): # defines configuration our application expects
    secret_key : str
    algorithm : str = "HS256"
    access_token_expire_minutes : int = 30
    redis_url : str = "redis://localhost:6379"
    database_url : str
    
    model_config = SettingsConfigDict(
        env_file = ".env"
    )

# instead of randomly accessing env variables thoughtout our code using os.getenv(..) 
# we have structured configuration object.
settings = Settings() # type: ignore