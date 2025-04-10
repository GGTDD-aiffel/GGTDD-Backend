from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserContext(BaseModel):
    user_context_id: str
    user_id: str
    default_context_id: Optional[str] = None
    context_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    