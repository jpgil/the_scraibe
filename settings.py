from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""

    azure_openai_api_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment_name: str = ""
    azure_openai_api_version: str = ""
    
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"

    class Config:
        # Loads variables from a .env file in the current directory
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()
