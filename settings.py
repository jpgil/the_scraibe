from pydantic_settings import BaseSettings # NEW
#
class Settings(BaseSettings):
    # Private keys for LLM providers
    openai_api_key: str = ""
    gemini_api_key: str = ""
    
    # Choose the LLM provider: "openai" or "gemini"
    llm_provider: str = "openai"
    
    llm_model: str = "gpt-4o"

    class Config:
        # Loads variables from a .env file in the current directory
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()
