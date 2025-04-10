from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class ActionableStepContextTagRepository(BaseRepository):
    """
    액션 스텝과 컨텍스트/태그 연결 정보에 접근하는 레포지토리 클래스
    """
    
    def get_step_ids_by_context_and_tag(
        self, 
        user_id: str, 
        context_ids: Optional[List[str]] = None, 
        tag_ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        컨텍스트 ID와 태그 ID로 액션 스텝 ID 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            context_ids: 컨텍스트 ID 목록 (옵션)
            tag_ids: 태그 ID 목록 (옵션)
            
        Returns:
            액션 스텝 ID 목록
        """
        print("\n=== ContextTagRepository Debug ===")
        print(f"Input - user_id: {user_id}")
        print(f"context_ids: {context_ids}")
        print(f"tag_ids: {tag_ids}")
        
        query = self.db.collection('actionable_step_context_tags').where('user_id', '==', user_id)
        
        if context_ids and tag_ids:
            print("Filtering by both context_ids and tag_ids")
            query = (query
                    .where('user_context_id', 'in', context_ids)
                    .where('user_tag_id', 'in', tag_ids))
        elif context_ids:
            print("Filtering by context_ids only")
            query = query.where('user_context_id', 'in', context_ids)
        elif tag_ids:
            print("Filtering by tag_ids only")
            query = query.where('user_tag_id', 'in', tag_ids)
        
        print("Executing query...")
        docs = query.stream()
        step_ids = list(set([doc.to_dict()['actionable_step_id'] for doc in docs]))
        print(f"Found step_ids: {step_ids}")
        print("=== End ContextTagRepository Debug ===\n")
        
        return step_ids
    
    def get_context_tags_by_step_id(self, step_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        액션 스텝 ID로 연결된 컨텍스트와 태그 정보를 조회합니다.
        
        Args:
            step_id: 액션 스텝 ID
            user_id: 사용자 ID
            
        Returns:
            컨텍스트와 태그 정보 목록
        """
        query = (self.db.collection('actionable_step_context_tags')
                .where('actionable_step_id', '==', step_id)
                .where('user_id', '==', user_id))
        
        docs = query.stream()
        return [self._convert_timestamp_to_iso(doc.to_dict()) for doc in docs] 