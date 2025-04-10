from typing import Dict, Any, List, Optional
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class TempActionableStepRepository(BaseRepository):
    """
    임시 액션 단계 데이터에 접근하는 레포지토리 클래스
    """
    
    def create_temp_step(self, data: Dict[str, Any]) -> str:
        """
        임시 액션 단계를 생성합니다.
        
        Args:
            data: 저장할 데이터
            
        Returns:
            생성된 문서의 ID
        """
        doc_ref = self.db.collection('temp_actionable_steps').add(data)
        return doc_ref[1].id
    
    def create_multiple_temp_steps(self, steps_data: List[Dict[str, Any]]) -> List[str]:
        """
        여러 임시 액션 단계를 한 번에 생성합니다.
        
        Args:
            steps_data: 저장할 데이터 목록
            
        Returns:
            생성된 문서 ID 목록
        """
        ids = []
        for data in steps_data:
            step_id = self.create_temp_step(data)
            ids.append(step_id)
        return ids
    
    def get_temp_step(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        특정 ID의 임시 액션 단계를 조회합니다.
        
        Args:
            doc_id: 문서 ID
            
        Returns:
            조회된 데이터 또는 None
        """
        doc_ref = self.db.collection('temp_actionable_steps').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_temp_steps_by_recognition_id(self, recognition_id: str) -> List[Dict[str, Any]]:
        """
        인식 ID에 해당하는 모든 임시 액션 단계를 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            조회된 임시 액션 단계 목록
        """
        query = self.db.collection('temp_actionable_steps').where('recognition_id', '==', recognition_id)
        docs = query.get()
        
        result = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            result.append(data)
        
        return result