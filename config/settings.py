from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GIGACHAT_API_KEY: str = Field(title='API ключ к модели GigaChat')
    GIGACHAT_MODEL_NAME: str = Field(title='Название модели GigaChat')
    GIGACHAT_BASE_URL: str = Field(title='Адрес API модели GigaChat')
    GIGACHAT_VERIFY_SSL_CERTS: bool = Field(title='Необходимость проверки сертификатов')
    TEMPERATURE: float = Field(default=0, title='Температура модели')
    
    class Config:
        env_file = '.env'
        
settings = Settings()