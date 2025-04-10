from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from firebase_admin import firestore

class ActionableStepRepository(BaseRepository):
    """
    액션 스텝 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def create_actionable_step(self, step_data: Dict[str, Any]) -> str:
        """
        액션 스텝을 생성합니다.
        
        Args:
            step_data: 생성할 액션 스텝 데이터
            
        Returns:
            생성된 액션 스텝 ID
        """
        if 'created_at' not in step_data:
            step_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('actionable_steps').add(step_data)
        return doc_ref[1].id
    
    def get_actionable_step(self, step_id: str) -> Optional[Dict[str, Any]]:
        """
        액션 스텝을 조회합니다.
        
        Args:
            step_id: 액션 스텝 ID
            
        Returns:
            액션 스텝 정보 또는 None
        """
        doc = self.db.collection('actionable_steps').document(step_id).get()
        return self._doc_to_dict(doc)
    
    def get_actionable_steps(self, user_id: str, page: int, limit: int, 
                            context_names: Optional[List[str]] = None, 
                            tag_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        조건에 맞는 액션 스텝 목록을 페이지네이션하여 조회합니다.
        
        Args:
            user_id: 사용자 ID
            page: 페이지 번호 (1부터 시작)
            limit: 페이지당 항목 수
            context_names: 필터링할 컨텍스트 이름 목록 (옵션)
            tag_names: 필터링할 태그 이름 목록 (옵션)
            
        Returns:
            액션 스텝 목록과 페이지네이션 메타 정보를 포함한 딕셔너리
        """
        # 컨텍스트 ID 조회
        user_context_ids = []
        if context_names:
            context_query = (self.db.collection('user_contexts')
                            .where('user_id', '==', user_id)
                            .where('context_name', 'in', context_names[:10]))
            user_context_ids = [doc.id for doc in context_query.get()]
        
        # 태그 ID 조회
        user_tag_ids = []
        if tag_names:
            tag_query = (self.db.collection('user_tags')
                        .where('user_id', '==', user_id)
                        .where('tag_name', 'in', tag_names[:10]))
            user_tag_ids = [doc.id for doc in tag_query.get()]
        
        # 액션 스텝-컨텍스트-태그 연결 정보로 액션 스텝 ID 조회
        step_ids_query = self.db.collection('actionable_step_context_tags').where('user_id', '==', user_id)
        
        if user_context_ids and user_tag_ids:
            step_ids_query = step_ids_query.where('user_context_id', 'in', user_context_ids).where('user_tag_id', 'in', user_tag_ids)
        elif user_context_ids:
            step_ids_query = step_ids_query.where('user_context_id', 'in', user_context_ids)
        elif user_tag_ids:
            step_ids_query = step_ids_query.where('user_tag_id', 'in', user_tag_ids)
    
        step_ids = list(set([doc.to_dict()['actionable_step_id'] for doc in step_ids_query.stream()]))

        if not step_ids:
            return {
                "data": [],
                "meta": {
                    "current_page": page,
                    "total_pages": 0,
                    "total_items": 0,
                    "limit": limit
                }
            }
        
        # 전체 아이템 수 조회
        total_query = (self.db.collection('actionable_steps')
                      .where('user_id', '==', user_id)
                      .where('id', 'in', step_ids))
        total_count = len(list(total_query.stream()))
        
        # 액션 스텝 조회
        steps_query = (self.db.collection('actionable_steps')
                      .where('user_id', '==', user_id)
                      .where('id', 'in', step_ids)
                      .limit(limit))

        # 페이지네이션 처리
        if page > 1:
            prev_query = steps_query.limit((page - 1) * limit)
            last_doc = list(prev_query.stream())[-1] if list(prev_query.stream()) else None
            if last_doc:
                steps_query = steps_query.start_after(last_doc)

        # 결과 가공
        steps_data = []
        for doc in steps_query.stream():
            step_dict = doc.to_dict()
            step_dict['id'] = doc.id

            # 관련 컨텍스트, 태그 정보 조회
            context_tags_query = (self.db.collection('actionable_step_context_tags')
                                 .where('actionable_step_id', '==', doc.id)
                                 .where('user_id', '==', user_id))
            context_tags = [tag.to_dict() for tag in context_tags_query.stream()]

            step_dict['context_tags'] = context_tags
            steps_data.append(self._convert_timestamp_to_iso(step_dict))
            
        # 페이지네이션 정보
        total_pages = (total_count + limit - 1) // limit  # 올림 나눗셈
        
        return {
            "data": steps_data,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_count,
                "limit": limit
            }
        }
    
    def link_step_to_context_tag(self, link_data: Dict[str, Any]) -> str:
        """
        액션 스텝과 컨텍스트/태그를 연결합니다.
        
        Args:
            link_data: 연결 데이터 (actionable_step_id, user_id, user_context_id, user_tag_id 등)
            
        Returns:
            생성된 연결 ID
        """
        if 'created_at' not in link_data:
            link_data['created_at'] = self._get_server_timestamp()
            
        doc_ref = self.db.collection('actionable_step_context_tags').add(link_data)
        return doc_ref[1].id 