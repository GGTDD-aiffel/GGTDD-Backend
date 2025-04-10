from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class UserTag(BaseModel):
  user_tag_id: str
  user_id: str
  default_tag_id: Optional[str] = None
  user_context_id: Optional[str] = None
  tag_name: str
  type: str
  category: Optional[str] = None
  description: Optional[str] = None
  bg_color: Optional[str] = None
  text_color: Optional[str] = None
  icon_name: Optional[str] = None
  created_at: datetime
  updated_at: Optional[datetime] = None
  

  