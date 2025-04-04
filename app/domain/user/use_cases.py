from app.domain.user.models import User
from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.firebase_utils import convert_firebase_timestamp, convert_firebase_MBTI
from app.infrastructure.LLMs.user_generator import UserGenerator

class UserUseCase:
    def __init__(self, llm_service: UserGenerator, repo: FirebaseRepository):
        self.repo = repo
        self.llm_service = llm_service
    
    def create_user(self, user_id: str):
        user_data = self.repo.get_user(user_id)

        user = User(**self._prepare_user_data(user_data, user_id))
        return user
    
    def _prepare_user_data(self, user_data, uid):
        return {
            'name': user_data['name'],
            'email': user_data['email'],
            'residence': user_data['residence'],
            'birth_date': convert_firebase_timestamp(user_data['birth_date']),
            'occupation': self.repo.get_occupation_name(user_data['occupation_id']),
            'personality': convert_firebase_MBTI(user_data['mbti']),
            'status': user_data['status'],
            'is_admin': user_data['is_admin'],
        }
    
    def select_prompt(self, user: User, prompt_index):
        """특정 프롬프트 선택"""
        if 0 <= prompt_index < len(user._prompts):
            user.selected_prompt = user._prompts[prompt_index]
            return user.selected_prompt
        raise ValueError("유효하지 않은 프롬프트 인덱스입니다")
    
    def update_tags(self, user: User):
        """선택된 프롬프트에서 태그 추출"""
        user.location_tags = self.collect_tags_by_type(user, "space")
        user.time_tags = self.collect_tags_by_type(user, "time")
        user.other_tags = self.collect_tags_by_type(user, "etc")
        
        return user.bio_str
    
    def collect_tags_by_type(self, user: User, tag_type: str):
        """사용자 태그 수집"""
        tags = self.repo.get_user_tags_by_type(user_id=user.uid, type=tag_type)
        tags_str_list = []
        
        for tag in tags:
            tag_str = f"{tag['tag_name']}({tag['category']})"
            tags_str_list.append(tag_str)
        
        return tags_str_list