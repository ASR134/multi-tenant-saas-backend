from pydantic_settings import BaseSettings, SettingsConfigDict

# pydantic BaseSettings does case-insensitive matching by default.
class Settings(BaseSettings): # defines configuration our application expects 
    secret_key : str
    algorithm : str 
    access_token_expire_minutes : int 
    redis_url : str 
    database_url : str
    
    model_config = SettingsConfigDict(
        env_file = ".env"
    )

# instead of randomly accessing env variables thoughtout our code using os.getenv(..) 
# we have structured configuration object.
settings = Settings() # type: ignore