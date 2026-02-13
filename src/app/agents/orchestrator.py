import yaml
from langchain_openai import ChatOpenAI
from src.app.core.token_logger import TokenEstimator
import json

with open("src/app/prompts/prompts.yml") as f:
    PROMPTS = yaml.safe_load(f)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def orchestrator(question: str) -> dict:
    estimator = TokenEstimator("orchestrator")

    system = PROMPTS["orchestrator"]["system"]
    user = PROMPTS["orchestrator"]["user_template"].format(question=question)
    prompt = system + "\n\n" + user

    estimator.log_text_estimated(prompt)
    response = llm.invoke(prompt)

    return json.loads(response.content)
