from app.domain.common.models import BaseResponse
from fastapi import APIRouter, Query
from app.domain.actionable_step.use_cases import ActionableStepUseCase
from app.domain.actionable_step.models import ActionableStep, ActionableStepResponse
from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.openai_service import OpenAIService
from typing import List, Optional, Union

router = APIRouter()
use_case = ActionableStepUseCase(FirebaseRepository(), OpenAIService())

@router.get("/api/actionable_steps", response_model=BaseResponse[ActionableStepResponse])
def get_actionable_steps(user_id: str, page: int = Query(1), limit: int = Query(10), context_names: Optional[List[str]] = Query(None), tag_names: Optional[List[str]] = Query(None)):
    return use_case.get_actionable_steps(user_id, page, limit, context_names, tag_names)

@router.get("/api/actionable_steps/today", response_model=list[ActionableStep])
def get_today_actionable_steps(user_id: str):
    return use_case.get_today_actionable_steps(user_id)

@router.get("/api/actionable_steps/now", response_model=Union[ActionableStep, None])
def get_current_actionable_step(user_id: str, current_time: str):
    return use_case.get_current_actionable_step(user_id, current_time)