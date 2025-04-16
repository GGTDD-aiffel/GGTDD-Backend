from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class RecognitionRepository(BaseRepository):
    """
    인식(Recognition) 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def get_recognition(self, recognition_id: str) -> Optional[Dict[str, Any]]:
        """
        인식 정보를 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            인식 정보 또는 None
        """
        recognition_doc = self.db.collection('recognitions').document(recognition_id).get()
        return self._doc_to_dict(recognition_doc)
    
    def create_recognition(self, recognition_data: Dict[str, Any]) -> str:
        """
        인식 정보를 생성합니다.
        
        Args:
            recognition_data: 생성할 인식 데이터
            
        Returns:
            생성된 인식 ID
        """
        if 'created_at' not in recognition_data:
            recognition_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('recognitions').add(recognition_data)
        return doc_ref[1].id
    
    def update_recognition(self, recognition_id: str, data: Dict[str, Any]) -> None:
        """
        인식 정보를 수정합니다.
        
        Args:
            recognition_id: 수정할 인식 ID
            data: 수정할 데이터
        """
        if 'updated_at' not in data:
            data['updated_at'] = self._get_server_timestamp()
            
        self.db.collection('recognitions').document(recognition_id).update(data)
    
    # 패러프레이즈 관련 메소드
    def create_paraphrase(self, paraphrase_data: Dict[str, Any]) -> str:
        """
        패러프레이즈를 생성합니다.
        
        Args:
            paraphrase_data: 생성할 패러프레이즈 데이터
            
        Returns:
            생성된 패러프레이즈 ID
        """
        if 'created_at' not in paraphrase_data:
            paraphrase_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('paraphrases').add(paraphrase_data)
        return doc_ref[1].id
    
    def get_paraphrases_by_recognition_id(self, recognition_id: str) -> List[Dict[str, Any]]:
        """
        인식 ID로 패러프레이즈 목록을 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            패러프레이즈 목록
        """
        query = (self.db.collection('paraphrases')
                .where('recognition_id', '==', recognition_id)
                .order_by('created_at'))
        
        docs = query.get()
        return self._docs_to_list(docs)
    
    def update_paraphrase(self, paraphrase_id: str, data: Dict[str, Any]) -> None:
        """
        패러프레이즈를 수정합니다.
        
        Args:
            paraphrase_id: 수정할 패러프레이즈 ID
            data: 수정할 데이터
        """
        if 'updated_at' not in data:
            data['updated_at'] = self._get_server_timestamp()
            
        self.db.collection('paraphrases').document(paraphrase_id).update(data)
    
    def select_paraphrase(self, paraphrase_id: str) -> None:
        """
        패러프레이즈를 선택 상태로 변경합니다.
        
        Args:
            paraphrase_id: 선택할 패러프레이즈 ID
        """
        self.update_paraphrase(paraphrase_id, {
            'is_selected_paraphrase': True,
            'updated_at': self._get_server_timestamp()
        })
    
    def delete_paraphrases_by_recognition_id(self, recognition_id: str) -> None:
        """
        인식 ID에 해당하는 모든 패러프레이즈를 삭제합니다.
        
        Args:
            recognition_id: 인식 ID
        """
        query = self.db.collection('paraphrases').where('recognition_id', '==', recognition_id)
        docs = query.get()
        for doc in docs:
            doc.reference.delete()
    
    # 추천 태그 관련 메소드
    def create_recommendation(self, recommendation_data: Dict[str, Any]) -> str:
        """
        추천 태그를 생성합니다.
        
        Args:
            recommendation_data: 생성할 추천 데이터
            
        Returns:
            생성된 추천 ID
        """
        if 'created_at' not in recommendation_data:
            recommendation_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('recommended_context_tags').add(recommendation_data)
        return doc_ref[1].id
    
    def get_recommendation_by_recognition_id(self, recognition_id: str) -> Optional[Dict[str, Any]]:
        """
        인식 ID로 추천 태그를 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            추천 태그 정보 또는 None
        """
        query = (self.db.collection('recommended_context_tags')
                .where('recognition_id', '==', recognition_id)
                .limit(1))
        
        docs = query.get()
        if docs and len(docs) > 0:
            return self._doc_to_dict(docs[0])
        return None
    
    def update_recognition_tags(self, tag_link_data: Dict[str, Any]) -> None:
        """
        인식에 태그 연결 정보를 업데이트합니다.
        
        Args:
            tag_link_data: 업데이트할 태그 연결 데이터
        """
        recognition_id = tag_link_data.pop('recognition_id', None)
        if not recognition_id:
            raise ValueError("recognition_id가 필요합니다.")
            
        if 'updated_at' not in tag_link_data:
            tag_link_data['updated_at'] = self._get_server_timestamp()
            
        self.db.collection('recognitions').document(recognition_id).update(tag_link_data)
    
    # 액션 스텝 관련 메소드
    def create_temp_actionable_step(self, temp_step_data: Dict[str, Any]) -> str:
        """
        임시 액션 스텝을 생성합니다.
        
        Args:
            temp_step_data: 생성할 임시 액션 스텝 데이터
            
        Returns:
            생성된 임시 액션 스텝 ID
        """
        if 'created_at' not in temp_step_data:
            temp_step_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('temp_actionable_steps').add(temp_step_data)
        return doc_ref[1].id
    
    def get_temp_actionable_steps(self, recognition_id: str) -> List[Dict[str, Any]]:
        """
        인식 ID로 임시 액션 스텝 목록을 조회합니다.
        
        Args:
            recognition_id: 인식 ID
            
        Returns:
            임시 액션 스텝 목록
        """
        query = (self.db.collection('temp_actionable_steps')
                .where('recognition_id', '==', recognition_id)
                .order_by('created_at'))
        
        docs = query.get()
        return self._docs_to_list(docs)
    
    def get_temp_actionable_step(self, temp_id: str) -> Optional[Dict[str, Any]]:
        """
        임시 액션 스텝을 조회합니다.
        
        Args:
            temp_id: 임시 액션 스텝 ID
            
        Returns:
            임시 액션 스텝 정보 또는 None
        """
        doc = self.db.collection('temp_actionable_steps').document(temp_id).get()
        return self._doc_to_dict(doc) 