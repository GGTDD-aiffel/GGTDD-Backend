from pydantic import BaseModel
from typing import List, Optional

class Inbox(BaseModel):
    content_id: str
    user_id: str
    content: str
    created_at: str
    updated_at: Optional[str] = None
    is_clarified: bool
    is_sent_to_recognition: bool

class PaginationMeta(BaseModel):
    current_page: int
    total_pages: int
    total_items: int
    limit: int

class InboxResponse(BaseModel):
    data: List[Inbox]
    meta: PaginationMeta