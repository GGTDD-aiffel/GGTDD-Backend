from app.domain.inbox.models import InboxResponse, Inbox, PaginationMeta
from app.domain.common.models import BaseResponse
from app.infrastructure.firebase_repo import FirebaseRepository
import logging
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InboxUseCase:
    def __init__(self, repo: FirebaseRepository):
        self.repo = repo

    def get_inboxes(self, user_id: str, page: int, limit: int, is_sent_to_recognition: bool) -> BaseResponse[InboxResponse]:
        try:
            raw_data = self.repo.get_inboxes(user_id, page, limit, is_sent_to_recognition)
            
            # 받은 원시 데이터 로깅
            logger.info(f"Raw data from Firebase: {json.dumps(raw_data, default=str)}")
            
            inbox_list = [Inbox(**item) for item in raw_data["data"]]
            pagination_meta = PaginationMeta(**raw_data["meta"])
            
            inbox_response = InboxResponse(data=inbox_list, meta=pagination_meta)
            
            # InboxResponse 객체 로깅
            logger.info(f"InboxResponse object: {inbox_response.json()}")
            
            response = BaseResponse[InboxResponse](
                code=200,
                status="success",
                message="Inbox 조회 성공",
                data=inbox_response
            )
            
            # 최종 응답 객체 로깅
            logger.info(f"Final response: {response.json()}")
            
            return response
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            return BaseResponse[InboxResponse](
                code=400,
                status="error",
                message=f"잘못된 입력: {str(e)}",
                data=None
            )
        except Exception as e:
            logger.error(f"Exception: {str(e)}", exc_info=True)
            return BaseResponse[InboxResponse](
                code=500,
                status="error",
                message=f"Inbox 조회 실패: {str(e)}",
                data=None
            )