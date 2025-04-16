from typing import List, Dict, Any, Optional
from app.domain.common.models import BaseResponse
from app.infrastructure.repository.user_tags_repository import UserTagRepository
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserTagUseCase:
    def __init__(self, repo: UserTagRepository):
        self.repo = repo
    
    def get_user_tags(self, user_id: str) -> BaseResponse[List[Dict[str, Any]]]:
        """
        사용자의 모든 태그를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 태그 목록
        """
        try:
            tags = self.repo.get_user_tags(user_id)
            return BaseResponse[List[Dict[str, Any]]](
                code=200,
                status="success",
                message="사용자 태그 조회 성공",
                data=tags
            )
        except Exception as e:
            logger.error(f"사용자 태그 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[List[Dict[str, Any]]](
                code=500,
                status="error",
                message=f"사용자 태그 조회 실패: {str(e)}",
                data=[]
            )
    
    def get_user_tag_names(self, user_id: str) -> List[str]:
        """
        사용자 태그 이름 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 태그 이름 목록
        """
        try:
            tags = self.repo.get_user_tags(user_id)
            return [tag['tag_name'] for tag in tags] if tags else []
        except Exception as e:
            logger.error(f"사용자 태그 이름 조회 중 오류 발생: {str(e)}", exc_info=True)
            return []
    
    def get_user_tag_names_str(self, user_id: str) -> str:
        """
        사용자 태그 이름 목록을 콤마로 구분된 문자열로 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            콤마로 구분된 사용자 태그 이름 문자열
        """
        try:
            tag_names = self.get_user_tag_names(user_id)
            return ", ".join(tag_names) if tag_names else ""
        except Exception as e:
            logger.error(f"사용자 태그 이름 문자열 조회 중 오류 발생: {str(e)}", exc_info=True)
            return ""
    
    def get_user_tags_by_type(self, user_id: str, tag_type: str) -> BaseResponse[List[Dict[str, Any]]]:
        """
        특정 타입의 사용자 태그를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            tag_type: 태그 타입 (location, time, other 등)
            
        Returns:
            해당 타입의 사용자 태그 목록
        """
        try:
            tags = self.repo.get_user_tags_by_type(user_id, tag_type)
            return BaseResponse[List[Dict[str, Any]]](
                code=200,
                status="success",
                message=f"{tag_type} 타입의 사용자 태그 조회 성공",
                data=tags
            )
        except Exception as e:
            logger.error(f"사용자 태그 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[List[Dict[str, Any]]](
                code=500,
                status="error",
                message=f"사용자 태그 조회 실패: {str(e)}",
                data=[]
            )
    
    def collect_tags_by_type(self, user_id: str, tag_type: str) -> List[str]:
        """
        특정 타입의 사용자 태그를 수집하여 문자열 리스트로 반환합니다.
        
        Args:
            user_id: 사용자 ID
            tag_type: 태그 타입
            
        Returns:
            태그 문자열 리스트
        """
        try:
            tags = self.repo.get_user_tags_by_type(user_id, tag_type)
            tags_str_list = []
            
            for tag in tags:
                if 'category' in tag and tag['category']:
                    tag_str = f"{tag['tag_name']}({tag['category']})"
                else:
                    tag_str = tag['tag_name']
                    
                tags_str_list.append(tag_str)
            
            return tags_str_list
        except Exception as e:
            logger.error(f"사용자 태그 수집 중 오류 발생: {str(e)}", exc_info=True)
            return []
    
    def create_user_tag(self, user_id: str, tag_name: str, tag_type: str, 
                       category: Optional[str] = None) -> BaseResponse[str]:
        """
        사용자 태그를 생성합니다.
        
        Args:
            user_id: 사용자 ID
            tag_name: 태그 이름
            tag_type: 태그 타입
            category: 태그 카테고리 (optional)
            
        Returns:
            생성된 태그 ID
        """
        try:
            tag_data = {
                'user_id': user_id,
                'tag_name': tag_name,
                'tag_type': tag_type,
                'category': category
            }
            tag_id = self.repo.create_user_tag(tag_data)
            
            return BaseResponse[str](
                code=201,
                status="success",
                message="사용자 태그 생성 성공",
                data=tag_id
            )
        except Exception as e:
            logger.error(f"사용자 태그 생성 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[str](
                code=500,
                status="error",
                message=f"사용자 태그 생성 실패: {str(e)}",
                data=""
            )
    
    def get_tag_id_by_name(self, user_id: str, tag_name: str) -> Optional[str]:
        """
        태그 이름으로 태그 ID를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            tag_name: 태그 이름
            
        Returns:
            태그 ID 또는 None
        """
        try:
            return self.repo.get_user_tag_id(user_id, tag_name)
        except Exception as e:
            logger.error(f"태그 ID 조회 중 오류 발생: {str(e)}", exc_info=True)
            return None
    
    def get_tag_ids_by_names(self, user_id: str, tag_names: List[str], tag_type: str) -> List[str]:
        """
        태그 이름 목록으로 태그 ID 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            tag_names: 태그 이름 목록
            tag_type: 태그 타입
            
        Returns:
            태그 ID 목록
        """
        try:
            tag_ids = []
            created_tags = []
            
            for tag_name in tag_names:
                # 기존 태그 조회
                tag_id = self.repo.get_user_tag_id(user_id, tag_name)
                
                # 태그가 없으면 새로 생성
                if not tag_id:
                    tag_data = {
                        'user_id': user_id,
                        'tag_name': tag_name,
                        'tag_type': tag_type
                    }
                    tag_id = self.repo.create_user_tag(tag_data)
                    created_tags.append(tag_name)
                
                tag_ids.append(tag_id)
            
            # 새로 생성된 태그가 있으면 로깅
            if created_tags:
                logger.info(f"새로 생성된 {tag_type} 태그: {', '.join(created_tags)}")
                
            return tag_ids
        except Exception as e:
            logger.error(f"태그 ID 목록 조회 중 오류 발생: {str(e)}", exc_info=True)
            return []
    
    def get_formatted_user_tags(self, user_id: str) -> str:
        """
        사용자의 태그 목록을 'ID: 이름(타입)' 형식의 문자열로 반환합니다.
        LLM 프롬프트에 사용하기 적합한 형태입니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            형식화된 태그 문자열 (예: "tag_id1: 공부(other), tag_id2: 집(location)")
        """
        try:
            tags_data = self.repo.get_user_tags(user_id)
            if not tags_data:
                return "사용자 태그 정보 없음"
            
            formatted_tags = []
            for tag in tags_data:
                tag_id = tag.get('id', 'NO_ID')
                tag_name = tag.get('tag_name', 'NO_NAME')
                tag_type = tag.get('tag_type', 'unknown') 
                formatted_tags.append(f"{tag_id}: {tag_name}({tag_type})")
                
            return ", ".join(formatted_tags)
        except Exception as e:
            logger.error(f"사용자 태그 포맷팅 중 오류 발생: {str(e)}", exc_info=True)
            return "태그 정보 로드 오류"