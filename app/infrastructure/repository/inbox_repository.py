from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class InboxRepository(BaseRepository):
    """
    인박스 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def get_inbox(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        인박스 항목 하나를 조회합니다.
        
        Args:
            content_id: 인박스 항목 ID
            
        Returns:
            인박스 항목 정보 또는 None
        """
        inbox_doc = self.db.collection('inbox').document(content_id).get()
        return self._doc_to_dict(inbox_doc)
    
    def get_inboxes(self, user_id: str, page: int, limit: int, is_sent_to_recognition: bool) -> Dict[str, Any]:
        """
        사용자의 인박스 항목을 페이지네이션하여 조회합니다.
        
        Args:
            user_id: 사용자 ID
            page: 페이지 번호 (1부터 시작)
            limit: 페이지당 항목 수
            is_sent_to_recognition: 인식 전송 여부
            
        Returns:
            인박스 항목 및 페이지네이션 정보를 포함한 딕셔너리
        """
        query = (self.db.collection('inbox')
                .where('user_id', '==', user_id)
                .where('is_sent_to_recognition', '==', is_sent_to_recognition)
                .order_by('created_at', direction=firestore.Query.ASCENDING)
                .limit(limit)
                .offset((page - 1) * limit))
        
        docs = query.get()
        data = [
            {
                "content_id": doc.id,
                **self._convert_timestamp_to_iso(doc.to_dict())
            } for doc in docs
        ]

        # 전체 항목 수 조회
        total_query = (self.db.collection('inbox')
                      .where('user_id', '==', user_id)
                      .where('is_sent_to_recognition', '==', is_sent_to_recognition))
        total_docs = total_query.get()
        total_items = len(total_docs)
        total_pages = (total_items + limit - 1) // limit if limit > 0 else 1

        return {
            "data": data,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "limit": limit
            }
        }