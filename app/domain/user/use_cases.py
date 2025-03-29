from app.domain.user.models import User
from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.firebase_utils import convert_firebase_timestamp, convert_firebase_MBTI
from app.infrastructure.LLMs.UserGenerator import UserGenerator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


class UserUseCase:
    def __init__(self, repo: FirebaseRepository, llm_service: UserGenerator):
        self.repo = repo
        self.llm_service = llm_service
    
    def create_user(self, user_id: str):
        user_data = self.repo.get_user(user_id)
        user_data['uid'] = user_id

        user = User(**self._prepare_user_data(user_data))
        return user
    
    def _prepare_user_data(self, user_data):
        return {
            'name': user_data['name'],
            'uid': user_data['uid'],
            'email': user_data['email'],
            'residence': user_data['residence'],
            'birth_date': convert_firebase_timestamp(user_data['birth_date']),
            'occupation': self.repo.get_occupation_name(user_data['occupation_id']),
            'personality': convert_firebase_MBTI(user_data['mbti']),
            'status': user_data['status'],
            'is_admin': user_data['is_admin'],
        }
        
    def collect_tags(self, user: User):
        tags = {
            'location_tags': user.location_tags,
            'time_tags': user.time_tags,
            'other_tags': user.other_tags
        }
        return tags