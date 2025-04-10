from typing import Dict, Any, List, Optional
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class RecommendedContextTagsRepository(BaseRepository):
    """
    추천된 컨텍스트 및 태그 정보에 접근하는 레포지토리 클래스
    """
    def create_recommended_tags(self, recognition_id: str, user_context_id: Optional[str], user_tag_id: Optional[str]) -> str:
        """
        추천된 컨텍스트 또는 태그 정보를 생성하고 Firestore에서 생성된 문서 ID를 반환합니다.
        문서 ID는 Firestore에서 자동으로 생성되며, 이 ID를 recommendationId로 사용합니다.
        
        Args:
            recognition_id: 연결된 Recognition ID
            user_context_id: 추천된 컨텍스트 ID (컨텍스트 추천 시 제공, 태그 추천 시 None)
            user_tag_id: 추천된 태그 ID (태그 추천 시 제공, 컨텍스트 추천 시 None)
            
        Returns:
            생성된 문서(추천)의 ID (recommendationId)
        """
        doc_ref = self.db.collection('recommended_context_tags').document()
        recommendation_id = doc_ref.id
        
        data = {
            'recognition_id': recognition_id,
            'user_context_id': user_context_id,
            'user_tag_id': user_tag_id,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        
        doc_ref.set(data)
        
        return recommendation_id
    
    def get_recommended_tags(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 ID(recommendationId)의 추천된 컨텍스트 및 태그 정보를 조회합니다.
        
        Args:
            doc_id: 문서 ID
            
        Returns:
            조회된 데이터 또는 None
        """
        doc_ref = self.db.collection('recommended_context_tags').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_recommended_tags_by_recognition_id(self, recognition_id: str) -> List[Dict[str, Any]]:
        """
        인식 ID에 해당하는 모든 추천 태그를 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            조회된 추천 태그 목록
        """
        query = self.db.collection('recommended_context_tags').where('recognition_id', '==', recognition_id)
        docs = query.get()
        
        result = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            result.append(data)
        
        return result