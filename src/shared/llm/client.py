import logging
from typing import Any, List, Optional

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM Client Supporting multiple providers
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.provider = provider or settings.LLM_PROVIDER
        self.model = model or self._get_default_model()
        self.temperature = temperature or settings.LLM_TEMPERATURE

        self._llm = None
        self._chat_model = None
        self._embeddings = None

    def _get_default_model(self) -> str:
        """Get default model based on provider"""
        if self.provider == "ollama":
            return settings.OLLAMA_MODEL
        elif self.provider == "openai":
            return "gpt-4"
        else:
            return settings.OLLAMA_MODEL

    def get_chat_model(self) -> ChatOllama:
        """
        Get Chat Model instance

        """
        if self._chat_model is None:
            if self.provider == "ollama":
                self._chat_model = ChatOllama(
                    model=self.model,
                    temperature=self.temperature,
                    num_ctx=settings.OLLAMA_NUM_CTX,
                )
            elif self.provider == "openai":
                self._chat_model = ChatOpenAI(
                    model=self.model,
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                    temperature=self.temperature,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")

            logger.info(
                f"Initialized LLM with provider: {self.provider}, model: {self.model}"
            )
        return self._chat_model

    def get_embeddings(self) -> OllamaEmbeddings:
        """
        Get LLM Embeddings
        """
        if self._embeddings is None:
            if self.provider == "ollama":
                self._embeddings = OllamaEmbeddings(
                    model=settings.OLLAMA_EMBEDDING_MODEL,
                    base_url=settings.OLLAMA_BASE_URL,
                )
            elif self.provider == "openai":
                self._embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL,
                )
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")

            logger.info(
                f"Initialized embeddings with provider: {self.provider}, model: {settings.OLLAMA_EMBEDDING_MODEL}"
            )
        return self._embeddings

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        **kwargs: Any,
    ):
        chat_model = self.get_chat_model()
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("human", prompt))

        response = await chat_model.ainvoke(messages, **kwargs)
        return response

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for list of texts
        """
        embeddings = self.get_embeddings()
        embedding = await embeddings.aembed_query(text)
        return embedding

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents
        """
        embeddings = self.get_embeddings()
        embedding_list = await embeddings.aembed_documents(texts)
        return embedding_list

    def embed(self, text: str):
        import asyncio

        return asyncio.run(self.embed_text(text))


llm_client = LLMClient()
