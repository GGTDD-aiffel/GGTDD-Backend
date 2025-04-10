from app.domain.actionable_step.models import ActionableStep, ActionableStepResponse, PaginationMeta
from app.domain.common.models import BaseResponse
from app.infrastructure.repository.actionable_step_repository import ActionableStepRepository
from app.infrastructure.openai_service import OpenAIService
from typing import List, Union, Optional
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionableStepUseCase:
    def __init__(self, repo: ActionableStepRepository, ai_service: Optional[OpenAIService] = None):
        self.repo = repo
        self.ai_service = ai_service

    def get_actionable_steps(self, user_id: str, page: int, limit: int, context_names: Optional[List[str]] = None, tag_names: Optional[List[str]] = None) -> BaseResponse[ActionableStepResponse]:
        """
        사용자의 액션 단계 목록을 조회합니다.
        
        Args:
            user_id: 사용자 ID
            page: 페이지 번호
            limit: 페이지당 항목 수
            context_names: 필터링할 컨텍스트 이름 목록
            tag_names: 필터링할 태그 이름 목록
            
        Returns:
            BaseResponse 객체로 래핑된 ActionableStepResponse
        """
        try:
            # 저장소에서 데이터 조회
            raw_data = self.repo.get_actionable_steps(user_id, page, limit, context_names, tag_names)
            
            # 데이터 모델로 변환
            steps = [ActionableStep(**item) for item in raw_data.get('data', [])]
            meta = PaginationMeta(**raw_data.get('meta', {
                'current_page': page,
                'total_pages': 1,
                'total_items': len(steps),
                'limit': limit
            }))
            
            response_data = ActionableStepResponse(data=steps, meta=meta)
            
            return BaseResponse[ActionableStepResponse](
                code=200,
                status="success",
                message="액션 단계 조회 성공",
                data=response_data
            )
        except Exception as e:
            logger.error(f"액션 단계 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[ActionableStepResponse](
                code=500,
                status="error",
                message=f"액션 단계 조회 실패: {str(e)}",
                data=None
            )

    def get_today_actionable_steps(self, user_id: str) -> BaseResponse[List[ActionableStep]]:
        """
        오늘의 추천 액션 단계를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            추천된 ActionableStep 목록
        """
        try:
            if not self.ai_service:
                return BaseResponse[List[ActionableStep]](
                    code=400,
                    status="error",
                    message="AI 서비스가 설정되지 않았습니다.",
                    data=[]
                )
                
            # 모든 미완료 항목 가져오기
            data = self.repo.get_actionable_steps(user_id, page=1, limit=100)
            steps = [item['step_content'] for item in data.get('data', []) if not item['is_completed']]
            
            if steps:
                recommended_steps = self.ai_service.recommend_actionable_steps(steps)
                # 추천된 순서대로 데이터 정렬
                result = []
                for step in recommended_steps:
                    for item in data.get('data', []):
                        if item['step_content'] == step:
                            result.append(ActionableStep(**item))
                
                return BaseResponse[List[ActionableStep]](
                    code=200,
                    status="success",
                    message="오늘의 액션 단계 조회 성공",
                    data=result
                )
            
            return BaseResponse[List[ActionableStep]](
                code=200,
                status="success",
                message="오늘의 액션 단계가 없습니다.",
                data=[]
            )
        except Exception as e:
            logger.error(f"오늘의 액션 단계 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[List[ActionableStep]](
                code=500,
                status="error",
                message=f"오늘의 액션 단계 조회 실패: {str(e)}",
                data=[]
            )
    
    def get_current_actionable_step(self, user_id: str, current_time: str) -> BaseResponse[Optional[ActionableStep]]:
        """
        현재 시간에 맞는 액션 단계를 조회합니다.
        
        Args:
            user_id: 사용자 ID
            current_time: 현재 시간 문자열
            
        Returns:
            추천된 ActionableStep 또는 None
        """
        try:
            if not self.ai_service:
                return BaseResponse[Optional[ActionableStep]](
                    code=400,
                    status="error",
                    message="AI 서비스가 설정되지 않았습니다.",
                    data=None
                )
                
            # 모든 미완료 항목 가져오기
            data = self.repo.get_actionable_steps(user_id, page=1, limit=100)
            steps = [item['step_content'] for item in data.get('data', []) if not item['is_completed']]
            
            if steps:
                recommended_step = self.ai_service.recommend_current_actionable_step(steps, current_time)
                for item in data.get('data', []):
                    if item['step_content'] == recommended_step:
                        return BaseResponse[Optional[ActionableStep]](
                            code=200,
                            status="success",
                            message="현재 시간에 맞는 액션 단계 조회 성공",
                            data=ActionableStep(**item)
                        )
            
            return BaseResponse[Optional[ActionableStep]](
                code=200,
                status="success",
                message="현재 시간에 맞는 액션 단계가 없습니다.",
                data=None
            )
        except Exception as e:
            logger.error(f"현재 액션 단계 조회 중 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[Optional[ActionableStep]](
                code=500,
                status="error",
                message=f"현재 액션 단계 조회 실패: {str(e)}",
                data=None
            )