from src.app.agents.risk_agent import risk_agent
from src.app.agents.orchestrator import orchestrator
from src.app.agents.extractor_agent import extractor_agent
from src.app.agents.qa_agent import qa_agent
import yaml

with open("src/app/prompts/prompts.yml", "r") as f:
    PROMPTS = yaml.safe_load(f)

def run_multi_agent(question: str):
    
    # 1) Segurança - Prompt Injection
    if risk_agent(question):
        return {
            "answer": PROMPTS["risk_agent"]["block_message"],
            "intent": "blocked",
            "metadata": {},
        }

    # 2) Orquestra Intenção + Filtros
    ork = orchestrator(question)
    intent = ork["intent"]
    metadata = ork.get("metadata_filters", {})

    # 3) Extrator (Busca no Chroma)
    context = extractor_agent(question, metadata)

    # 4) QA Agent (Resposta Final)
    final_answer = qa_agent(question, context)

    return {
        "answer": final_answer,
        "intent": intent,
        "metadata": metadata,
        "context": context,
    }
