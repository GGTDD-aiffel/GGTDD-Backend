from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.recognition.models import ParaphraseRequest, ParaphraseResponse
from firebase_admin import credentials, firestore

from typing import List

class RecognitionUseCase:
    def __init__(self, ai_service: RecognitionGenerator, repo: FirebaseRepository):
        self.ai_service = ai_service
        self.repo = repo

    def generate_paraphrase(self, request: ParaphraseRequest) -> ParaphraseResponse:
        """
        주어진 내용을 패러프레이즈하여 데이터베이스에 저장하고 반환합니다.
        
        Args:
            request: 패러프레이즈 요청 정보를 담은 Pydantic 모델
            
        Returns:
            생성된 패러프레이즈 목록을 담은 응답 객체
        """
        paraphrases_list = self.ai_service.generate_paraphrase(
            request.user_context, 
            request.content
        )
        
        for paraphrase in paraphrases_list:
            paraphrase_data = {
                'recognition_id': request.recognition_id,
                'paraphrase_content': paraphrase,
                'is_selected_paraphrase': False,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            # Save each paraphrase to the database
            self.repo.create_paraphrase(paraphrase_data)
        
        return ParaphraseResponse(paraphrases=paraphrases_list)

    def generate_recommended_context_tags(self, recognition_id: str, content: str, user_context: str):
        recommended_tags = self.ai_service.generate_context_tags(user_context, content)
        
        for tag in recommended_tags:
            print(tag)
            tag_data = {
                'recognition_id': recognition_id,
                'user_context_id': recommended_tags.get('context'),
                'user_tag_id': self.repo.get_user_tag_id(user_id=user_id, tag_name=tag),
                'created_at': firestore.SERVER_TIMESTAMP
            }
            self.repo.create_recommendation(tag_data)
        return recommended_tags

    # def generate_recommended_context_tags(self, recognition_id: str, content: str):
    #     recommendations = self.ai_service.generate_context_tags(content)
    #     recommendation_data = {
    #         'recognition_id': recognition_id,
    #         'user_context_id': recommendations.get('context'),
    #         'user_tag_id': recommendations.get('tags'),
    #         'created_at': firestore.SERVER_TIMESTAMP
    #     }
    #     self.repo.create_recommendation(recommendation_data)
    #     return recommendations
    
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