import yaml
import json
from langchain_openai import ChatOpenAI

from src.app.core.token_logger import TokenEstimator
from src.app.storage.chroma_store import ChromaHnswStore
from src.app.storage.embeddings import build_embeddings
from src.app.retrieval.chroma_retriever import ChromaRetriever

from src.app.core.utils import get_unique_companies, get_metadata_fields

with open("src/app/prompts/prompts.yml") as f:
    PROMPTS = yaml.safe_load(f)

planner_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

store = ChromaHnswStore()
embedder = build_embeddings()
retriever = ChromaRetriever(store=store, embeddings=embedder)


def extractor_agent(question: str, metadata_filters: dict):

    estimator = TokenEstimator("extractor_planner")

    # 1. coletar contexto do dataset
    metadata_fields = get_metadata_fields(store)
    company_values = get_unique_companies(store)

    # 2. montar mensagens completas
    messages = [
        {
            "role": "system",
            "content": PROMPTS["extractor_agent"]["system"]
        },
        {
            "role": "user",
            "content": PROMPTS["extractor_agent"]["user_template"].format(
                question=question,
                metadata=metadata_filters,
                metadata_fields=metadata_fields,
                company_values=company_values
            )
        }
    ]

    # log estimado
    estimator.log_estimated(messages)

    # 3. planner LLM → gera plano JSON
    llm_response = planner_llm.invoke(messages)
    plan = json.loads(llm_response.content)

    query_text = plan["query_embedding_text"]
    filters = plan["filters"]

    # 4. executa retrieval real
    retrieved = retriever.retrieve(
        query=query_text,
        metadata_filters=filters,
        top_k=10
    )

    # 5. concatena contexto
    context = "\n\n".join([item["text"] for item in retrieved])

    return context
