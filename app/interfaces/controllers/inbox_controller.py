from app.domain.common.models import BaseResponse
from fastapi import APIRouter, Query
from app.domain.inbox.use_cases import InboxUseCase
from app.domain.inbox.models import InboxResponse
from app.infrastructure.firebase_repo import FirebaseRepository

router = APIRouter()
use_case = InboxUseCase(FirebaseRepository())

@router.get("/api/inbox", response_model=BaseResponse[InboxResponse])
def get_inboxes(user_id: str = Query(...), page: int = Query(1), limit: int = Query(10)):
    return use_case.get_inboxes(user_id, page, limit, is_sent_to_recognition=False)