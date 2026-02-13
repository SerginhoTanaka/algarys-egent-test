import yaml
from langchain_openai import ChatOpenAI
from src.app.core.token_logger import TokenEstimator

with open("src/app/prompts/prompts.yml") as f:
    PROMPTS = yaml.safe_load(f)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def risk_agent(question: str) -> bool:
    estimator = TokenEstimator("risk_agent")

    prompt = PROMPTS["risk_agent"]["user_template"].format(question=question)
    system = PROMPTS["risk_agent"]["system"]
    classify = PROMPTS["risk_agent"]["classify_injection"]
    full_prompt = system + "\n\n" + prompt + "\n\n" + classify

    estimator.log_text_estimated(full_prompt)
    response = llm.invoke(full_prompt)

    verdict = response.content.strip().lower()
    return verdict == "high_risk"
