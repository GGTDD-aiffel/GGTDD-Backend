from typing import List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from google.type import datetime_pb2

class FirebaseRepository:
    def __init__(self):
        self.db = firestore.client()

    # inbox
    def get_inboxes(self, user_id: str, page: int, limit: int, is_sent_to_recognition: bool) -> dict:
        query = (self.db.collection('inbox')
                .where('user_id', '==', user_id)
                .where('is_sent_to_recognition', '==', is_sent_to_recognition)
                .order_by('created_at', direction=firestore.Query.ASCENDING)
                .limit(limit)
                .offset((page - 1) * limit))
        docs = query.get()
        data = [
            {
                "content_id": doc.id,
                **{k: v.isoformat() if hasattr(v, 'isoformat') else v for k, v in doc.to_dict().items()}
            } for doc in docs
        ]

        total_query = self.db.collection('inbox').where('user_id', '==', user_id)
        total_docs = total_query.get()
        total_items = len(total_docs)
        total_pages = (total_items + limit - 1) // limit

        return {
            "data": data,
            "meta": {
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "limit": limit
            }
        }
    
    def update_inbox(self, content_id: str, data: dict):
        self.db.collection('inbox').document(content_id).update(data)

    # recognitions
    def create_recognition(self, recognition_data: dict):
        self.db.collection('recognitions').add(recognition_data)

    # paraphrases
    def create_paraphrase(self, paraphrase_data: dict):
        self.db.collection('paraphrases').add(paraphrase_data)
        
    def delete_paraphrase_by_recognition_id(self, recognition_id: str):
        query = self.db.collection('paraphrases').where('recognition_id', '==', recognition_id)
        docs = query.get()
        for doc in docs:
            doc.reference.delete()

    # recommended_context_tags
    def create_recommendation(self, recommendation_data: dict):
        self.db.collection('recommended_context_tags').add(recommendation_data)

    # temp_actionable_steps
    def create_temp_actionable_step(self, temp_step_data: dict):
        self.db.collection('temp_actionable_steps').add(temp_step_data)

    def get_temp_actionable_step(self, temp_id: str) -> dict:
        return self.db.collection('temp_actionable_steps').document(temp_id).get().to_dict()

    def create_actionable_step(self, step_data: dict):
        self.db.collection('actionable_steps').add(step_data)

    def get_actionable_steps(self, user_id: str, page: int, limit: int, context_names: Optional[List[str]] = None, tag_names: Optional[List[str]] = None) -> list[dict]:
        user_context_ids = []
        if context_names:
            context_query = self.db.collection('user_contexts').where('user_id', '==', user_id).where('context_name', 'in', context_names[:10])
            user_context_ids = [doc.id for doc in context_query.get()]
        
        user_tag_ids = []
        if tag_names:
            tag_query = self.db.collection('user_tags').where('user_id' '==', user_id).where('tag_name', 'in', tag_names[:10])
            user_tag_ids = [doc.id for doc in tag_query.get()]
        
        step_ids_query = self.db.collection('actionable_step_context_tags').where('user_id', '==', user_id)
        if user_context_ids and user_tag_ids:
            step_ids_query = step_ids_query.where('user_context_id', 'in', user_context_ids).where('user_tag_id', 'in', user_tag_ids)
        elif user_context_ids:
            step_ids_query = step_ids_query.where('user_context_id', 'in', user_context_ids)
        elif user_tag_ids:
            step_ids_query = step_ids_query.where('user_tag_id', 'in', user_tag_ids)
    
        step_ids = list(set([doc.to_dict()['actionable_step_id'] for doc in step_ids_query.stream()]))

        if not step_ids:
            return []
        
        steps_query = self.db.collection('actionable_steps').where('user_id', '==', user_id).where('id', 'in', step_ids)
        steps_query = steps_query.order_by('created_at').limit(limit)

        if page > 1:
            prev_query = steps_query.limit((page - 1) * limit)
            last_doc = list(prev_query.stream())[-1]
            steps_query = steps_query.start_after(last_doc)

        steps_data = []
        for doc in steps_query.stream():
            step_dict = doc.to_dict()

            context_tags_query = self.db.collection('actionable_step_context_tags').where('actionable_step_id', '==', doc.id).where('user_id', '==', user_id)
            context_tags = [tag.to_dict() for tag in context_tags_query.stream()]

            step_dict['context_tags'] = context_tags
            steps_data.append(step_dict)

        return steps_data
    
    # user
    def get_user(self, user_id: str) -> dict:
        user = self.db.collection('users').document(user_id).get()
        return user.to_dict() if user.exists else None

    # occupations
    def get_occupation_name(self, occupation_id: str) -> str:
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
        
    # tags
    def get_user_tags_by_type(self, user_id: str, type: str) -> list:
        from firebase_admin import firestore
        
        tags_query = (self.db.collection('user_tags')
                     .where(filter=firestore.FieldFilter('user_id', '==', user_id))
                     .where(filter=firestore.FieldFilter('type', '==', type)))
        tags_docs = tags_query.get()
        return [doc.to_dict() for doc in tags_docs]
    
    def get_user_tag_id(self, user_id: str, tag_name: str) -> str:
        tag_query = (self.db.collection('user_tags')
                    .where(filter=firestore.FieldFilter('user_id', '==', user_id))
                    .where(filter=firestore.FieldFilter('tag_name', '==', tag_name)))
        tag_docs = tag_query.get()
        
        if tag_docs:
            return tag_docs[0].id
        else:
            return None
    
    def add_tag(self, tag_data: dict):
        self.db.collection('user_tags').add(tag_data)
    
    def get_user_tags(self, user_id: str) -> list:
        tags_query = (self.db.collection('user_tags')
                      .where(filter=firestore.FieldFilter('user_id', '==', user_id)))
        tags_docs = tags_query.get()
        
        return [doc.to_dict() for doc in tags_docs] if tags_docs else []
    
    def get_user_prompts(self, user_id: str) -> list:
        prompts_query = (self.db.collection('user_prompts')
                         .where(filter=firestore.FieldFilter('user_id', '==', user_id)))
        prompts_docs = prompts_query.get()
        
        return [doc.to_dict() for doc in prompts_docs] if prompts_docs else []