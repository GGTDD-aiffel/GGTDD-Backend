from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class UserContextRepository(BaseRepository):
    """
    사용자 컨텍스트 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def get_user_contexts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        사용자의 컨텍스트 정보를 조회하고, 각 컨텍스트 딕셔너리에 'id' 키로 문서 ID를 포함하여 반환합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            문서 ID가 포함된 사용자 컨텍스트 목록
        """
        contexts_query = (self.db.collection('user_contexts')
                         .where('user_id', '==', user_id))
        contexts_docs = contexts_query.get()
        
        results = []
        for doc in contexts_docs:
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
        return results
    
    def get_user_context_id(self, user_id: str, context_name: str) -> Optional[str]:
        """
        컨텍스트 이름으로 사용자 컨텍스트 ID를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            context_name: 컨텍스트 이름
            
        Returns:
            컨텍스트 ID 또는 None
        """
        context_query = (self.db.collection('user_contexts')
                         .where('user_id', '==', user_id)
                         .where('context_name', '==', context_name))
        context_docs = context_query.get()

        if context_docs:
            return context_docs[0].id
        return None
    
    def create_user_context(self, context_data: Dict[str, Any]) -> str:
      """
      사용자 컨텍스트를 생성합니다.
      
      Args:
          context_data: 생성할 컨텍스트 데이터
          
      Returns:
          생성된 컨텍스트 ID
      """
      doc_ref = self.db.collection('user_contexts').add(context_data)
      return doc_ref[1].id