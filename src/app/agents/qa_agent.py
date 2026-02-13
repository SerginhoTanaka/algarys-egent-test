import yaml
from langchain_openai import ChatOpenAI
from src.app.core.token_logger import TokenEstimator

with open("src/app/prompts/prompts.yml") as f:
    PROMPTS = yaml.safe_load(f)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def qa_agent(question: str, context: str):
    estimator = TokenEstimator("qa_agent")

    system = PROMPTS["qa_agent"]["system"]
    user = PROMPTS["qa_agent"]["user_template"].format(
        question=question,
        context=context
    )
    prompt = system + "\n\n" + user

    estimator.log_text_estimated(prompt)
    response = llm.invoke(prompt)
    return response.content
