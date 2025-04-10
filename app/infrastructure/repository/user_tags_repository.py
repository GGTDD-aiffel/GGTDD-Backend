from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class UserTagRepository(BaseRepository):
    """
    태그 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def get_user_tags(self, user_id: str) -> List[Dict[str, Any]]:
        """
        사용자의 모든 태그를 조회하고, 각 태그 딕셔너리에 'id' 키로 문서 ID를 포함하여 반환합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            문서 ID가 포함된 사용자 태그 목록
        """
        tags_query = (self.db.collection('user_tags')
                      .where('user_id', '==', user_id))
        tags_docs = tags_query.get()
        
        results = []
        for doc in tags_docs:
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
        return results
    
    def get_user_tag_id(self, user_id: str, tag_name: str) -> Optional[str]:
        """
        태그 이름으로 사용자 태그 ID를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            tag_name: 태그 이름
            
        Returns:
            태그 ID 또는 None
        """
        tag_query = (self.db.collection('user_tags')
                    .where('user_id', '==', user_id)
                    .where('tag_name', '==', tag_name))
        tag_docs = tag_query.get()
        
        if tag_docs:
            return tag_docs[0].id
        return None
    
    def get_user_tags_by_type(self, user_id: str, tag_type: str) -> List[Dict[str, Any]]:
        """
        특정 타입의 사용자 태그를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            tag_type: 태그 타입 (location, time, other 등)
            
        Returns:
            해당 타입의 사용자 태그 목록
        """
        tags_query = (self.db.collection('user_tags')
                     .where('user_id', '==', user_id)
                     .where('tag_type', '==', tag_type))
        tags_docs = tags_query.get()
        
        return self._docs_to_list(tags_docs)
    
    def get_tag_by_id(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """
        ID로 태그를 조회합니다.
        
        Args:
            tag_id: 태그 ID
            
        Returns:
            태그 정보 또는 None
        """
        tag_doc = self.db.collection('user_tags').document(tag_id).get()
        return self._doc_to_dict(tag_doc) 