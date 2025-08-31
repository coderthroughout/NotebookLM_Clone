"""
Configuration module for the research system.
Loads environment variables and provides configuration settings.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


class Config:
    """Configuration class for the research system."""
    
    # OpenAI API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_PROJECT_ID: str = os.getenv("OPENAI_PROJECT_ID", "")
    OPENAI_ORG_ID: str = os.getenv("OPENAI_ORG_ID", "")
    
    # OpenAI Model Configuration
    OPENAI_MODEL_GPT4: str = os.getenv("OPENAI_MODEL_GPT4", "gpt-4-turbo-preview")
    OPENAI_MODEL_GPT35: str = os.getenv("OPENAI_MODEL_GPT35", "gpt-3.5-turbo")
    OPENAI_MODEL_EMBEDDING: str = os.getenv("OPENAI_MODEL_EMBEDDING", "text-embedding-3-small")
    
    # SerpAPI Configuration
    SERPAPI_API_KEY: str = os.getenv("SERPAPI_API_KEY", "")
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "citations.db")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")
    
    # Research Pipeline Configuration
    DEFAULT_CREDIBILITY_THRESHOLD: float = float(os.getenv("DEFAULT_CREDIBILITY_THRESHOLD", "0.5"))
    DEFAULT_SEARCH_RESULTS: int = int(os.getenv("DEFAULT_SEARCH_RESULTS", "8"))
    DEFAULT_SEARCH_PROVIDER: str = os.getenv("DEFAULT_SEARCH_PROVIDER", "serpapi")
    
    # Vector Indexing Configuration
    VECTOR_MODEL_NAME: str = os.getenv("VECTOR_MODEL_NAME", "all-MiniLM-L6-v2")
    VECTOR_DIMENSION: int = int(os.getenv("VECTOR_DIMENSION", "384"))
    FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "vector_index.faiss")
    
    # Content Generation Configuration
    MAX_TOKENS_OUTLINE: int = int(os.getenv("MAX_TOKENS_OUTLINE", "1000"))
    MAX_TOKENS_SCRIPT: int = int(os.getenv("MAX_TOKENS_SCRIPT", "2000"))
    MAX_TOKENS_SLIDES: int = int(os.getenv("MAX_TOKENS_SLIDES", "1500"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
    DOMAIN_DELAY_SECONDS: float = float(os.getenv("DOMAIN_DELAY_SECONDS", "0.5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "research.log")
    
    @classmethod
    def validate_openai_config(cls) -> bool:
        """Validate that OpenAI configuration is complete."""
        required_keys = [cls.OPENAI_API_KEY, cls.OPENAI_PROJECT_ID, cls.OPENAI_ORG_ID]
        return all(required_keys) and all(key.strip() for key in required_keys)
    
    @classmethod
    def validate_serpapi_config(cls) -> bool:
        """Validate that SerpAPI configuration is complete."""
        return bool(cls.SERPAPI_API_KEY and cls.SERPAPI_API_KEY.strip())
    
    @classmethod
    def get_openai_client_config(cls) -> dict:
        """Get OpenAI client configuration."""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "project_id": cls.OPENAI_PROJECT_ID,
            "organization": cls.OPENAI_ORG_ID,
        }
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Print a summary of the current configuration."""
        print("🔧 Configuration Summary:")
        print(f"  📊 Database: {cls.DATABASE_PATH}")
        print(f"  🔍 Search Provider: {cls.DEFAULT_SEARCH_PROVIDER}")
        print(f"  🎯 Credibility Threshold: {cls.DEFAULT_CREDIBILITY_THRESHOLD}")
        print(f"  🤖 OpenAI Models: {cls.OPENAI_MODEL_GPT4}, {cls.OPENAI_MODEL_GPT35}")
        print(f"  🔢 Vector Model: {cls.VECTOR_MODEL_NAME} ({cls.VECTOR_DIMENSION}D)")
        print(f"  📝 Content Generation: {cls.MAX_TOKENS_OUTLINE}/{cls.MAX_TOKENS_SCRIPT}/{cls.MAX_TOKENS_SLIDES} tokens")
        print(f"  ⚡ Rate Limiting: {cls.DOMAIN_DELAY_SECONDS}s delay")


# Global configuration instance
config = Config()
