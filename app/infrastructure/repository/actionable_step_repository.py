from typing import List, Optional, Dict, Any
from app.infrastructure.repository.base_repository import BaseRepository
from app.infrastructure.repository.actionable_step_context_tag_repository import ActionableStepContextTagRepository
from firebase_admin import firestore

class ActionableStepRepository(BaseRepository):
    """
    액션 스텝 관련 데이터에 접근하는 레포지토리 클래스
    """
    
    def __init__(self):
        super().__init__()
        self.context_tag_repo = ActionableStepContextTagRepository()
    
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
        """
        print("\n=== Repository Debug ===")
        print(f"Input - user_id: {user_id}, page: {page}, limit: {limit}")
        print(f"context_names: {context_names}")
        print(f"tag_names: {tag_names}")
        
        if context_names is None and tag_names is None:
            print("No filtering required, proceeding with simple pagination")
            steps_query = self.db.collection('actionable_steps').where('user_id', '==', user_id).where('is_completed', '==', False).order_by('created_at', direction=firestore.Query.ASCENDING)
            
            all_docs = list(steps_query.stream())
            print(f"Total documents in collection: {len(all_docs)}")
            print(f"First few documents: {[doc.id for doc in all_docs[:5]]}")
            
            total_count = len(all_docs)
            print(f"Total steps found: {total_count}")
            
            steps_query = steps_query.limit(limit)
            if page > 1:
                prev_query = steps_query.limit((page - 1) * limit)
                prev_docs = list(prev_query.stream())
                print(f"Previous page documents count: {len(prev_docs)}")
                last_doc = prev_docs[-1] if prev_docs else None
                if last_doc:
                    steps_query = steps_query.start_after(last_doc)
            
            current_docs = list(steps_query.stream())
            print(f"Filtered documents (is_completed == False): {[doc.id for doc in current_docs]}")
            print(f"Current page documents count: {len(current_docs)}")
            print(f"Current page document IDs: {[doc.id for doc in current_docs]}")
            
            steps_data = []
            for doc in current_docs:
                step_dict = doc.to_dict()
                step_dict['actionable_step_id'] = doc.id
                print(f"Processing document {doc.id}: {step_dict}")
                
                steps_data.append(self._convert_timestamp_to_iso(step_dict))
            
            total_pages = (total_count + limit - 1) // limit
            
            return {
                "data": steps_data,
                "meta": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_items": total_count,
                    "limit": limit
                }
            }
        
        user_context_ids = None
        if context_names:
            print(f"Querying contexts for names: {context_names}")
            context_query = (self.db.collection('user_contexts')
                            .where('user_id', '==', user_id)
                            .where('context_name', 'in', context_names))
            context_docs = list(context_query.get())
            if context_docs:
                user_context_ids = [doc.id for doc in context_docs]
            print(f"Found context IDs: {user_context_ids}")
        
        user_tag_ids = None
        if tag_names:
            print(f"Querying tags for names: {tag_names}")
            tag_query = (self.db.collection('user_tags')
                        .where('user_id', '==', user_id)
                        .where('tag_name', 'in', tag_names))
            tag_docs = list(tag_query.get())
            if tag_docs:
                user_tag_ids = [doc.id for doc in tag_docs]
            print(f"Found tag IDs: {user_tag_ids}")
        
        step_ids = None
        if user_context_ids or user_tag_ids:
            print(f"Querying step IDs with context_ids: {user_context_ids}, tag_ids: {user_tag_ids}")
            step_ids = self.context_tag_repo.get_step_ids_by_context_and_tag(
                user_context_ids, user_tag_ids
            )
            print(f"Found step IDs: {step_ids}")
            if not step_ids:
                print("No step IDs found, returning empty result")
                return {
                    "data": [],
                    "meta": {
                        "current_page": page,
                        "total_pages": 0,
                        "total_items": 0,
                        "limit": limit
                    }
                }
        
        steps_data = []
        if step_ids:
            print(f"Filtering steps by document IDs: {step_ids}")
            for step_id in step_ids:
                doc_ref = self.db.collection('actionable_steps').document(step_id)
                doc = doc_ref.get()
                if doc.exists and doc.to_dict().get('user_id') == user_id:
                    step_dict = doc.to_dict()
                    step_dict['actionable_step_id'] = doc.id
                    steps_data.append(self._convert_timestamp_to_iso(step_dict))
                    print(f"Processing document {doc.id}: {step_dict}")
            
            total_count = len(steps_data)
            print(f"Total steps found: {total_count}")
            
            steps_data = steps_data[(page-1)*limit : page*limit]
        else:
            steps_query = self.db.collection('actionable_steps').where('user_id', '==', user_id).where('is_completed', '==', False).order_by('created_at', direction=firestore.Query.ASCENDING).limit(limit)
            steps_data = [self._convert_timestamp_to_iso(doc.to_dict()) for doc in steps_query.stream()]
            total_count = len(steps_data)
            print(f"Total steps found: {total_count}")
        
        print(f"Final steps data count: {len(steps_data)}")
        print("=== End Repository Debug ===\n")
        
        total_pages = (total_count + limit - 1) // limit
        
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