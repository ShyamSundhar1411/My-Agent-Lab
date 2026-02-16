from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "My Agent Lab"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 9000
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str = "neo4j"
    VECTOR_INDEX_NAME: str = "KnowledgeEmbeddings"
    VECTOR_NODE_LABEL: str = "Chunk"
    VECTOR_SOURCE_PROPERTY: str = "text"
    VECTOR_EMBEDDING_PROPERTY: str = "embedding"
    LLM_PROVIDER: Literal["ollama", "openai", "anthropic"] = "ollama"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:latest"
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_TEMPERATURE: float = 0.0
    OLLAMA_NUM_CTX: int = 8192
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = "https://api.openai.com/v1"
    EMBEDDING_PROVIDER: Literal["ollama", "openai"] = "ollama"
    EMBEDDING_DIMENSIONS: int = 768
    LLM_TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 2000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
