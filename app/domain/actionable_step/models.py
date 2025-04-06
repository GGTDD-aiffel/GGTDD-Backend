from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ActionableStep(BaseModel):
    actionable_step_id: str
    content_id: str
    step_content: str
    is_completed: bool
    review: str
    created_at: str
    updated_at: Optional[str] = None

class PaginationMeta(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    limit: int
    
class ActionableStepResponse(BaseModel):
    data: List[ActionableStep]
    meta: PaginationMeta