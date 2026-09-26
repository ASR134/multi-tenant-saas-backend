from pydantic_settings import BaseSettings, SettingsConfigDict

# pydantic BaseSettings does case-insensitive matching by default.
class Settings(BaseSettings): # defines configuration our application expects 
    secret_key : str
    algorithm : str 
    access_token_expire_minutes : int 
    redis_url : str 
    celery_redis_url : str
    database_url : str
    email_verification_token_expire_minutes : int
    login_email_ip_limit : int
    login_ip_limit : int
    login_window : int
    resend_api_key : str
    email_from : str
    frontend_url : str
    password_reset_token_expire_minutes : int
    invitation_token_expire_days : int

    model_config = SettingsConfigDict(
        env_file = ".env",
        extra="ignore"
    )

# instead of randomly accessing env variables thoughtout our code using os.getenv(..) 
# we have structured configuration object.
settings = Settings() # type: ignore