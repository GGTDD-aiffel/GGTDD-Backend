from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class UserRepository(BaseRepository):
    """
    사용자 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        사용자 정보를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 정보 딕셔너리 또는 None
        """
        user_doc = self.db.collection('users').document(user_id).get()
        return self._doc_to_dict(user_doc)
    
    def get_occupation_name(self, occupation_id: str) -> str:
        """
        직업 ID로 직업명을 조회합니다.
        
        Args:
            occupation_id: 직업 ID
            
        Returns:
            직업명
        """
        if not occupation_id:
            return "Unknown"
        
        try:
            doc = self.db.collection('occupations').document(occupation_id).get()
            if doc.exists:
                return doc.to_dict().get('occupation_name', "Unknown")
            return "Unknown"
        except Exception as e:
            print(f"직업명 조회 중 오류 발생: {e}")
            return "Unknown" 