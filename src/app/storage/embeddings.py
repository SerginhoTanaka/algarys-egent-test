from typing import List
from src.app.config.settings import settings


class EmbeddingsProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError


class OpenAIEmbeddingProvider(EmbeddingsProvider):
    """
    Usa o embedding mais barato da OpenAI: text-embedding-3-small
    via LangChain.
    """
    def __init__(self):
        from langchain_openai import OpenAIEmbeddings

        kwargs = {
            "model": settings.openai_embedding_model, 
        }


        self.model = OpenAIEmbeddings(**kwargs)

    def embed(self, texts: List[str]) -> List[List[float]]:
        # LangChain faz batching automaticamente
        return self.model.embed_documents(texts)


class LocalSentenceTransformerEmbeddings(EmbeddingsProvider):
    """
    Mantenho seu embedding local original caso queira rodar offline.
    """
    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return vectors.tolist()


def build_embeddings() -> EmbeddingsProvider:
    """
    Fabrica um provider baseado no settings.embedding_provider.
    """
    provider = settings.embedding_provider.lower()

    if provider == "openai":
        return OpenAIEmbeddingProvider()

    if provider == "local":
        return LocalSentenceTransformerEmbeddings(settings.local_embedding_model)

    raise ValueError(f"Embedding provider não suportado: {provider}")
