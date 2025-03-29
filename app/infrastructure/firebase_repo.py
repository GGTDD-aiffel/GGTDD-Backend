import firebase_admin
from firebase_admin import credentials, firestore
from google.type import datetime_pb2

firebase_admin.initialize_app(credentials.Certificate('firebase/serviceAccountKey.json'))

# Cloud Run에서 마운트된 파일 경로 사용
# FIRESTORE_KEY_PATH = "/secrets/serviceAccountKey.json"
# firebase_admin.initialize_app(credentials.Certificate(FIRESTORE_KEY_PATH))

"""
gcloud run deploy fastapi-firestore \
    --image gcr.io/[PROJECT-ID]/fastapi-firestore:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-secrets "/secrets/serviceAccountKey.json=firebase-service-account:latest"
"""

class FirebaseRepository:
    def __init__(self):
        self.db = firestore.client()

    # inbox
    def get_inboxes(self, user_id: str, page: int, limit: int) -> dict:
        query = (self.db.collection('inbox')
                .where('user_id', '==', user_id)
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