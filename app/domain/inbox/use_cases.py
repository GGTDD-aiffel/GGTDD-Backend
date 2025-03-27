from app.domain.inbox.models import InboxResponse
from app.infrastructure.firebase_repo import FirebaseRepository

class InboxUseCase:
    def __init__(self, repo: FirebaseRepository):
        self.repo = repo

    def get_inboxes(self, user_id: str, page: int, limit: int) -> InboxResponse:
        data = self.repo.get_inboxes(user_id, page, limit)
        return InboxResponse(**data)

    def send_to_recognition(self, content_id: str):
        self.repo.update_inbox(content_id, {'is_sent_to_recognition': True})
        recognition_data = {
            'content_id': content_id,
            'created_at': self.repo.db.SERVER_TIMESTAMP,
            'is_processed': False
        }
        self.repo.create_recognition(recognition_data)