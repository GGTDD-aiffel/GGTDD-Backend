from app.domain.actionable_step.models import ActionableStep
from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.openai_service import OpenAIService
from typing import Union, Optional

class ActionableStepUseCase:
    def __init__(self, repo: FirebaseRepository, ai_service: Optional[OpenAIService] = None):
        self.repo = repo
        self.ai_service = ai_service

    def get_actionable_steps(self, user_id: str, page: int, limit: int) -> list[ActionableStep]:
        data = self.repo.get_actionable_steps(user_id, page, limit)
        return [ActionableStep(**item) for item in data]

    def get_today_actionable_steps(self, user_id: str) -> list[ActionableStep]:
        if not self.ai_service:
            raise ValueError("AI service is required for recommending actionable steps")
        data = self.repo.get_actionable_steps(user_id, page=1, limit=100)  # 모든 미완료 항목 가져오기
        steps = [item['step_content'] for item in data if not item['is_completed']]
        if steps:
            recommended_steps = self.ai_service.recommend_actionable_steps(steps)
            # 추천된 순서대로 데이터 정렬 (간단히 첫 번째 추천만 반환 예시)
            for step in recommended_steps:
                for item in data:
                    if item['step_content'] == step:
                        return [ActionableStep(**item)]
        return []
    
    def get_current_actionable_step(self, user_id: str, current_time: str) -> Union[ActionableStep, None]:
        if not self.ai_service:
            raise ValueError("AI service is required for recommending actionable steps")
        data = self.repo.get_actionable_steps(user_id, page=1, limit=100)
        steps = [item['step_content'] for item in data if not item['is_completed']]
        if steps:
            recommended_step = self.ai_service.recommend_current_actionable_step(steps, current_time)
            for item in data:
                if item['step_content'] == recommended_step:
                    return ActionableStep(**item)
        return None