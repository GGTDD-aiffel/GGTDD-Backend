import firebase_admin
from firebase_admin import credentials, firestore
from google.type import datetime_pb2

firebase_admin.initialize_app(credentials.Certificate('/app/env/firebase/serviceAccountKey.json'))

class FirebaseRepository:
    def __init__(self):
        self.db = firestore.client()

    # inbox
    def get_inboxes(self, user_id: str, page: int, limit: int) -> dict:
        query = (self.db.collection('inbox')
                .where('user_id', '==', user_id)
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

    # recommended_context_tags
    def create_recommendation(self, recommendation_data: dict):
        self.db.collection('recommended_context_tags').add(recommendation_data)

    # temp_actionable_steps
    def create_temp_actionable_step(self, temp_step_data: dict):
        self.db.collection('temp_actionable_steps').add(temp_step_data)

    def get_temp_actionable_step(self, temp_id: str) -> dict:
        return self.db.collection('temp_actionable_steps').document(temp_id).get().to_dict()

    # actionable_steps
    def create_actionable_step(self, step_data: dict):
        self.db.collection('actionable_steps').add(step_data)

    def get_actionable_steps(self, user_id: str, page: int, limit: int) -> list[dict]:
        inbox_query = self.db.collection('inbox').where('user_id', '==', user_id)
        content_ids = [doc.id for doc in inbox_query.get()]
        query = (self.db.collection('actionable_steps')
                .where('content_id', 'in', content_ids)
                .order_by('created_at')
                .limit(limit)
                .offset((page - 1) * limit))
        return [doc.to_dict() for doc in query.get()]