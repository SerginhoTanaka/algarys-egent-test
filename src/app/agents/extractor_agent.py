import yaml
import json
from langchain_openai import ChatOpenAI

from src.app.core.token_logger import TokenEstimator
from src.app.storage.chroma_store import ChromaHnswStore
from src.app.storage.embeddings import build_embeddings
from src.app.retrieval.chroma_retriever import ChromaRetriever

with open("src/app/prompts/prompts.yml") as f:
    PROMPTS = yaml.safe_load(f)

planner_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

store = ChromaHnswStore()
embedder = build_embeddings()
retriever = ChromaRetriever(store=store, embeddings=embedder)


def extractor_agent(question: str, metadata_filters: dict):
    """
    1. Usa LLM para criar um plano de busca (query text)
    2. Usa retriever para consultar Chroma
    3. Retorna contexto consolidado
    """
    estimator = TokenEstimator("extractor_planner")

    # 1) Mensagem para gerar plano de busca
    messages = [
        {"role": "system", "content": PROMPTS["extractor_agent"]["system"]},
        {"role": "user", "content": PROMPTS["extractor_agent"]["user_template"].format(
            question=question,
            metadata=metadata_filters
        )}
    ]

    # Log estimado (antes da chamada ao modelo)
    estimator.log_estimated(messages)

    # Chamada real do LLM
    llm_response = planner_llm.invoke(messages)
    plan = json.loads(llm_response.content)

    query_text = plan["query_embedding_text"]
    filters = plan["filters"]  # ainda não sanitizado → sanitiza no retriever

    # 2) Busca no Chroma usando a implementação correta
    retrieved = retriever.retrieve(
        query=query_text,
        metadata_filters=filters,
        top_k=10
    )

    # 3) Concatenação final do contexto
    context = "\n\n".join([item["text"] for item in retrieved])

    return context
