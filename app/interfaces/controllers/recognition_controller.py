from fastapi import APIRouter

from app.infrastructure.openai_service import OpenAIService
from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.recognition.use_cases import RecognitionUseCase

router = APIRouter()
use_case = RecognitionUseCase(OpenAIService(), FirebaseRepository())

@router.post("/api/paraphrase")
def generate_paraphrase(recognition_id: str, content: str, user_context: str):
    return use_case.generate_paraphrase(recognition_id, content, user_context)

@router.post("/api/recommended/context_tags")
def generate_recommended_context_tags(recognition_id: str, content: str, user_context: str):
    return use_case.generate_recommended_context_tags(recognition_id, content, user_context)

@router.post("/api/temp_actionable_steps")
def generate_temp_actionable_steps(recognition_id: str, content: str):
    return use_case.generate_temp_actionable_steps(recognition_id, content)

@router.post("/api/actionable_steps/save")
def save_actionable_steps(temp_step_ids: list[str], content_id: str):
    use_case.save_actionable_steps(temp_step_ids, content_id)
    return {"message": "Actionable steps saved"}