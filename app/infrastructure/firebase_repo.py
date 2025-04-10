from typing import List, Optional
from firebase_admin import firestore

class FirebaseRepository:
    def __init__(self):
        self.db = firestore.client()

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