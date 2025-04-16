from typing import List, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
import logging

logger = logging.getLogger(__name__)

class ParaphraseRepository(BaseRepository):
    """
    패러프레이즈 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def create_paraphrase(self, paraphrase_data: dict) -> str:
        """
        패러프레이즈 데이터를 데이터베이스에 저장합니다.
        
        Args:
            paraphrase_data: 패러프레이즈 데이터
            
        Returns:
            생성된 패러프레이즈 ID
        """
        doc_ref = self.db.collection('paraphrases').add(paraphrase_data)
        return doc_ref[1].id
    
    def create_bulk_paraphrases(self, paraphrases_data: List[Dict[str, Any]]) -> int:
        """
        여러 패러프레이즈 데이터를 데이터베이스에 일괄 저장합니다.
        Firestore의 WriteBatch를 사용하여 효율성을 높입니다.
        
        Args:
            paraphrases_data: 저장할 패러프레이즈 데이터 딕셔너리의 리스트
            
        Returns:
            성공적으로 저장된 패러프레이즈 문서의 수
        """
        batch = self.db.batch()
        paraphrase_collection = self.db.collection('paraphrases')
        count = 0
        
        for data in paraphrases_data:
            doc_ref = paraphrase_collection.document() 
            batch.set(doc_ref, data)
            count += 1
            
        batch.commit()
        
        return count
    
    def get_paraphrases_by_recognition_id(self, recognition_id: str) -> List[Dict[str, Any]]:
        """
        특정 recognition_id에 해당하는 모든 패러프레이즈를 조회합니다.
        
        Args:
            recognition_id: 조회할 인식 ID
            
        Returns:
            패러프레이즈 데이터 리스트
        """
        paraphrases = []
        try:
            query = self.db.collection('paraphrases').where('recognition_id', '==', recognition_id)
            docs = query.stream()
            
            for doc in docs:
                paraphrase_data = doc.to_dict()
                paraphrase_data['id'] = doc.id
                paraphrases.append(paraphrase_data)
                
            return paraphrases
        except Exception as e:
            logger.error(f"패러프레이즈 조회 중 오류 발생: {str(e)}", exc_info=True)
            return []
        
    
    
    
