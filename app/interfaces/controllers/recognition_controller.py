from fastapi import APIRouter
from langchain_openai import ChatOpenAI

from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.recognition.use_cases import RecognitionUseCase
from app.domain.recognition.models import (
    ParaphraseRequest,
    RecommendationRequest,
    TempActionableStepsRequest,
)

router = APIRouter()
recognitionGenerator = RecognitionGenerator(ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5))
use_case = RecognitionUseCase(recognitionGenerator, FirebaseRepository())

@router.post("/api/paraphrase")
def generate_paraphrase(request: ParaphraseRequest):
    return use_case.generate_paraphrase(request)

@router.post("/api/recommended/context_tags")
def generate_recommended_context_tags(request: RecommendationRequest):
    return use_case.generate_recommended_context_tags(request)

@router.post("/api/temp_actionable_steps")
def generate_temp_actionable_steps(request: TempActionableStepsRequest):
    return use_case.generate_temp_actionable_steps(request)

# @router.post("/api/actionable_steps/save")
# def save_actionable_steps(temp_step_ids: list[str], content_id: str):
#     use_case.save_actionable_steps(temp_step_ids, content_id)
#     return {"message": "Actionable steps saved"}