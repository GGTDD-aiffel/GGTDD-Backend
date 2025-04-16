from app.domain.common.models import BaseResponse
from fastapi import APIRouter, Query
from app.domain.actionable_step.use_cases import ActionableStepUseCase
from app.domain.actionable_step.models import ActionableStep, ActionableStepResponse
from app.infrastructure.repository.actionable_step_repository import ActionableStepRepository
from app.infrastructure.openai_service import OpenAIService
from typing import List, Optional, Union

router = APIRouter()
use_case = ActionableStepUseCase(ActionableStepRepository(), OpenAIService())

@router.get("/api/actionable_steps", response_model=BaseResponse[ActionableStepResponse])
def get_actionable_steps(
    user_id: str, 
    page: int = Query(1), 
    limit: int = Query(10), 
    context_names: Optional[str] = Query(None), 
    tag_names: Optional[str] = Query(None)
):
    print("\n=== Controller Debug ===")
    print(f"Received request - user_id: {user_id}, page: {page}, limit: {limit}")
    print(f"Raw context_names: {context_names}")
    print(f"Raw tag_names: {tag_names}")
    
    context_list = [x.strip() for x in context_names.split(',')] if context_names and context_names.strip() else None
    tag_list = [x.strip() for x in tag_names.split(',')] if tag_names and tag_names.strip() else None
    
    print(f"Processed context_list: {context_list}")
    print(f"Processed tag_list: {tag_list}")
    
    if context_list:
        context_list = [x for x in context_list if x]
        if not context_list:
            context_list = None
            
    if tag_list:
        tag_list = [x for x in tag_list if x]
        if not tag_list:
            tag_list = None
    
    print(f"Final context_list: {context_list}")
    print(f"Final tag_list: {tag_list}")
    print("=== End Controller Debug ===\n")
    
    return use_case.get_actionable_steps(user_id, page, limit, context_list, tag_list)

@router.get("/api/actionable_steps/today", response_model=list[ActionableStep])
def get_today_actionable_steps(user_id: str):
    return use_case.get_today_actionable_steps(user_id)

@router.get("/api/actionable_steps/now", response_model=Union[ActionableStep, None])
def get_current_actionable_step(user_id: str, current_time: str):
    return use_case.get_current_actionable_step(user_id, current_time)