from fastapi import APIRouter
from pydantic import BaseModel
from src.app.agents.pipeline import run_multi_agent

router = APIRouter(prefix="/ask", tags=["Ask"])

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    intent: str | None = None
    metadata_used: dict | None = None

@router.post("/", response_model=AskResponse)
def ask_question(payload: AskRequest):

    result = run_multi_agent(payload.question)

    return AskResponse(
        answer=result.get("answer"),
        intent=result.get("intent"),
        metadata_used=result.get("metadata"),
    )
