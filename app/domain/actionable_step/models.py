from pydantic import BaseModel

class ActionableStep(BaseModel):
    actionable_step_id: str
    content_id: str
    step_content: str
    is_completed: bool