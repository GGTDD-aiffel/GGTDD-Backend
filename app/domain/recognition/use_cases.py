from app.infrastructure.openai_service import OpenAIService
from app.infrastructure.firebase_repo import FirebaseRepository
from firebase_admin import credentials, firestore

class RecognitionUseCase:
    def __init__(self, ai_service: OpenAIService, repo: FirebaseRepository):
        self.ai_service = ai_service
        self.repo = repo

    def generate_paraphrase(self, recognition_id: str, content: str) -> str:
        paraphrase_content = self.ai_service.generate_paraphrase(content)
        paraphrase_data = {
            'recognition_id': recognition_id,
            'paraphrase_content': paraphrase_content,
            'is_selected_paraphrase': False,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        self.repo.create_paraphrase(paraphrase_data)
        return paraphrase_content
    
    def generate_recommended_context_tags(self, recognition_id: str, content: str):
        recommendations = self.ai_service.generate_context_tags(content)
        recommendation_data = {
            'recognition_id': recognition_id,
            'user_context_id': recommendations.get('context'),
            'user_tag_id': recommendations.get('tags'),
            'created_at': firestore.SERVER_TIMESTAMP
        }
        self.repo.create_recommendation(recommendation_data)
        return recommendations
    
    def generate_temp_actionable_steps(self, recognition_id: str, content: str):
        steps = self.ai_service.generate_temp_actionable_steps(content)
        for step in steps:
            temp_step_data = {
                'recognition_id': recognition_id,
                'step_content': step,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.repo.create_temp_actionable_step(temp_step_data)
        return steps
    
    def save_actionable_steps(self, temp_step_ids: list[str], content_id: str):
        for temp_id in temp_step_ids:
            temp_step = self.repo.get_temp_actionable_step(temp_id)
            if temp_step:
                actionable_step_data = {
                    'content_id': content_id,
                    'step_content': temp_step['step_content'],
                    'is_completed': False,
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'updated_at': None
                }
                self.repo.create_actionable_step(actionable_step_data)