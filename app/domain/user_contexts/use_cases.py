from typing import List, Dict, Any, Optional
from app.domain.common.models import BaseResponse
from app.domain.user_contexts.models import UserContext
from app.infrastructure.repository.user_repository import UserRepository
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserContextUseCase:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    def get_user_contexts(self, user_id: str) -> BaseResponse[List[UserContext]]:
        """
        사용자의 컨텍스트 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 컨텍스트 목록
        """
        try:
            contexts_data = self.repo.get_user_contexts(user_id)
            contexts = [UserContext(**context) for context in contexts_data]
            
            return BaseResponse[List[UserContext]](
                code=200,
                status="success",
                message="사용자 컨텍스트 조회 성공",
                data=contexts
            )
        except Exception as e:
            logger.error(f"사용자 컨텍스트 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[List[UserContext]](
                code=500,
                status="error",
                message=f"사용자 컨텍스트 조회 실패: {str(e)}",
                data=[]
            )
    
    def get_user_context_names(self, user_id: str) -> List[str]:
        """
        사용자 컨텍스트 이름 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 컨텍스트 이름 목록
        """
        try:
            contexts = self.repo.get_user_contexts(user_id)
            return [context['context_name'] for context in contexts] if contexts else []
        except Exception as e:
            logger.error(f"사용자 컨텍스트 이름 조회 중 오류 발생: {str(e)}", exc_info=True)
            return []
    
    def get_user_context_names_str(self, user_id: str) -> str:
        """
        사용자 컨텍스트 이름 목록을 콤마로 구분된 문자열로 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            콤마로 구분된 사용자 컨텍스트 이름 문자열
        """
        try:
            context_names = self.get_user_context_names(user_id)
            return ", ".join(context_names) if context_names else ""
        except Exception as e:
            logger.error(f"사용자 컨텍스트 이름 문자열 조회 중 오류 발생: {str(e)}", exc_info=True)
            return ""
    
    def get_user_context(self, context_id: str) -> BaseResponse[Optional[UserContext]]:
        """
        컨텍스트 ID로 컨텍스트를 조회합니다.
        
        Args:
            context_id: 컨텍스트 ID
            
        Returns:
            컨텍스트 정보 또는 None
        """
        try:
            context_data = self.repo.get_user_context(context_id)
            if not context_data:
                return BaseResponse[Optional[UserContext]](
                    code=404,
                    status="error",
                    message="컨텍스트를 찾을 수 없습니다.",
                    data=None
                )
            
            context = UserContext(**context_data)
            return BaseResponse[Optional[UserContext]](
                code=200,
                status="success",
                message="컨텍스트 조회 성공",
                data=context
            )
        except Exception as e:
            logger.error(f"컨텍스트 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[Optional[UserContext]](
                code=500,
                status="error",
                message=f"컨텍스트 조회 실패: {str(e)}",
                data=None
            )
    
    def create_user_context(self, user_id: str, context_name: str, default_context_id: Optional[str] = None) -> BaseResponse[str]:
        """
        사용자 컨텍스트를 생성합니다.
        
        Args:
            user_id: 사용자 ID
            context_name: 컨텍스트 이름
            default_context_id: 기본 컨텍스트 ID (optional)
            
        Returns:
            생성된 컨텍스트 ID
        """
        try:
            context_data = {
                'user_id': user_id,
                'context_name': context_name,
                'default_context_id': default_context_id,
            }
            context_id = self.repo.create_user_context(context_data)
            
            return BaseResponse[str](
                code=201,
                status="success",
                message="사용자 컨텍스트 생성 성공",
                data=context_id
            )
        except Exception as e:
            logger.error(f"사용자 컨텍스트 생성 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[str](
                code=500,
                status="error",
                message=f"사용자 컨텍스트 생성 실패: {str(e)}",
                data=""
            )
    
    def get_context_id_by_name(self, user_id: str, context_name: str) -> Optional[str]:
        """
        컨텍스트 이름으로 컨텍스트 ID를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            context_name: 컨텍스트 이름
            
        Returns:
            컨텍스트 ID 또는 None
        """
        try:
            return self.repo.get_user_context_id(user_id, context_name)
        except Exception as e:
            logger.error(f"컨텍스트 ID 조회 중 오류 발생: {str(e)}", exc_info=True)
            return None
            
    def get_context_ids_by_names(self, user_id: str, context_names: List[str]) -> List[str]:
        """
        컨텍스트 이름 목록으로 컨텍스트 ID 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            context_names: 컨텍스트 이름 목록
            
        Returns:
            컨텍스트 ID 목록
        """
        try:
            context_ids = []
            for name in context_names:
                context_id = self.repo.get_user_context_id(user_id, name)
                if context_id:
                    context_ids.append(context_id)
            return context_ids
        except Exception as e:
            logger.error(f"컨텍스트 ID 목록 조회 중 오류 발생: {str(e)}", exc_info=True)
            return []
        
    def get_formatted_user_contexts(self, user_id: str) -> str:
        """
        사용자의 컨텍스트 목록을 'ID: 이름' 형식의 문자열로 반환합니다.
        LLM 프롬프트에 사용하기 적합한 형태입니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            형식화된 컨텍스트 문자열 (예: "context_id1: 집, context_id2: 회사")
        """
        try:
            contexts_data = self.repo.get_user_contexts(user_id)
            if not contexts_data:
                return "사용자 컨텍스트 정보 없음"
            
            formatted_contexts = [f"{context.get('id', 'NO_ID')}: {context.get('context_name', 'NO_NAME')}" for context in contexts_data]
            return ", ".join(formatted_contexts)
        except Exception as e:
            logger.error(f"사용자 컨텍스트 포맷팅 중 오류 발생: {str(e)}", exc_info=True)
            return "컨텍스트 정보 로드 오류"
        
    