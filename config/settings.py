from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MODEL_NAME: str = Field(title='Название модели')
    MODEL_API_KEY: str = Field(title='API ключ к модели с OpenRouter')
    MODEL_API_BASE: str = Field(title='Адрес API OpenRouter', default='https://openrouter.ai/api/v1')
    TEMPERATURE: float = Field(default=0, title='Температура модели')
    
    class Config:
        env_file = '.env'
        
settings = Settings()