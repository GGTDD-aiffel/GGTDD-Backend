from typing import Dict, Any, Optional
from app.domain.common.models import BaseResponse
from app.domain.user.models import User, UserRequest, UserPromptsResponse
from app.infrastructure.firebase_utils import convert_firebase_timestamp, convert_firebase_MBTI
from app.infrastructure.LLMs.user_generator import UserGenerator
from app.infrastructure.repository.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class UserUseCase:
    def __init__(self, llm_service: UserGenerator, repo: UserRepository):
        self.repo = repo
        self.llm_service = llm_service
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        사용자 정보를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 정보 또는 None
        """
        return self.repo.get_user(user_id)
    
    def prepare_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 데이터를 User 모델에 맞게 가공합니다.
        
        Args:
            user_data: 원본 사용자 데이터
            
        Returns:
            가공된 사용자 데이터
        """
        try:
            # 필수 필드에 대한 기본값 설정
            birth_date = convert_firebase_timestamp(user_data.get('birth_date'))
            occupation = self.repo.get_occupation_name(user_data.get('occupation_id')) or '알 수 없음'
            personality = convert_firebase_MBTI(user_data.get('mbti', ''))
            
            # user_prompts 필드 처리 - 문자열로 유지
            user_prompts = user_data.get('user_prompts', '')
            # 리스트인 경우 문자열로 조인
            if isinstance(user_prompts, list):
                user_prompts = '\n'.join(user_prompts)
            # None인 경우 빈 문자열로 설정
            elif user_prompts is None:
                user_prompts = ''
            
            return {
                'name': user_data.get('name', ''),
                'email': user_data.get('email', ''),
                'residence': user_data.get('residence', ''),
                'birth_date': birth_date,
                'occupation': occupation,
                'personality': personality,
                'status': user_data.get('status', ''),
                'is_admin': user_data.get('is_admin', False),
                'is_premium': user_data.get('is_premium', False),
                'user_prompts': user_prompts,
            }
        except Exception as e:
            logger.error(f"사용자 데이터 가공 중 오류 발생: {str(e)}", exc_info=True)
            # 최소한의 필수 데이터만 반환
            return {
                'name': user_data.get('name', '알 수 없음'),
                'email': user_data.get('email', ''),
                'residence': user_data.get('residence', ''),
                'birth_date': None,
                'occupation': '알 수 없음',
                'personality': [],
                'status': user_data.get('status', ''),
                'is_admin': False,
                'is_premium': False,
                'user_prompts': '',
            }
    
    def create_user_instance(self, user_id: str) -> Optional[User]:
        """
        사용자 ID로부터 User 모델 인스턴스를 생성합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            User 모델 인스턴스 또는 None(사용자 정보가 없는 경우)
        """
        user_data = self.get_user(user_id)
        if not user_data:
            return None
            
        prepared_data = self.prepare_user_data(user_data)
        return User(**prepared_data)
    
    def generate_user_prompts(self, user_id: str) -> BaseResponse[UserPromptsResponse]:
        """
        사용자 정보를 기반으로 프롬프트를 생성합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            생성된 프롬프트 응답
        """
        user = self.create_user_instance(user_id)
        if not user:
            return BaseResponse[UserPromptsResponse](
                code=404,
                status="error",
                message="사용자 정보를 찾을 수 없습니다.",
                data=None
            )
        
        prompts_response = self.llm_service.generate_prompts_and_tags(user)
        
        return BaseResponse[UserPromptsResponse](
            code=200,
            status="success",
            message="프롬프트 생성 성공",
            data=prompts_response
        )
    
    