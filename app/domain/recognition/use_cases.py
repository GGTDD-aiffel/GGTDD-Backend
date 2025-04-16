import logging
from app.domain.user.use_cases import UserUseCase
from app.domain.user_contexts.use_cases import UserContextUseCase
from app.domain.user_tags.use_cases import UserTagUseCase
from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.domain.common.models import BaseResponse
from app.domain.recognition.models import (
    ParaphraseRequest,
    ParaphraseResponse,
    RecommendationRequest,
    RecommendationResponse,
    TempActionableStepsRequest,
    TempActionableStepsResponse
)

from firebase_admin import firestore
from typing import List, Optional

from app.infrastructure.repository.paraphrase_repository import ParaphraseRepository
from app.infrastructure.repository.recommended_context_tags_repository import RecommendedContextTagsRepository
from app.infrastructure.repository.temp_acitonable_step_repository import TempActionableStepRepository

logger = logging.getLogger(__name__)

class RecognitionUseCase:
    def __init__(
        self, 
        ai_service: RecognitionGenerator, 
        paraphrase_repo: ParaphraseRepository,
        recommended_repo: RecommendedContextTagsRepository,
        temp_step_repo: TempActionableStepRepository,
        user_use_case: UserUseCase,
        tag_use_case: UserTagUseCase,
        context_use_case: UserContextUseCase
    ):
        self.ai_service = ai_service
        self.paraphrase_repo = paraphrase_repo
        self.recommended_repo = recommended_repo
        self.temp_step_repo = temp_step_repo
        self.user_use_case = user_use_case
        self.tag_use_case = tag_use_case
        self.context_use_case = context_use_case

    def generate_paraphrase(self, request: ParaphraseRequest) -> BaseResponse[ParaphraseResponse]:
        """
        주어진 내용을 패러프레이즈하여 데이터베이스에 저장하고 반환합니다.
        
        Args:
            request: 패러프레이즈 요청 정보를 담은 Pydantic 모델
            
        Returns:
            생성된 패러프레이즈 목록을 담은 응답 객체
        """
        user = self.user_use_case.create_user_instance(request.user_id)
        if not user:
            return BaseResponse[ParaphraseResponse](
                code=404,
                status="error",
                message="사용자 정보를 찾을 수 없습니다.",
                data=None
            )
         
        contexts_str = self.context_use_case.get_user_context_names_str(request.user_id)
        tags_str = self.tag_use_case.get_user_tag_names_str(request.user_id)
        
        paraphrases_response = self.ai_service.generate_paraphrase(
            user.bio_str, 
            contexts_str, 
            tags_str,     
            request.content
        )
        
        paraphrase_docs = []
        for paraphrase in paraphrases_response.paraphrases:
            paraphrase_data = {
                'recognition_id': request.recognition_id,
                'paraphrase_content': paraphrase,
                'is_selected_paraphrase': False,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            paraphrase_docs.append(paraphrase_data)
            
        if paraphrase_docs:
             self.paraphrase_repo.create_bulk_paraphrases(paraphrase_docs)
        
        response = BaseResponse[ParaphraseResponse](
            code=200,
            status="success",
            message="Paraphrase 반환 성공",
            data=ParaphraseResponse(
                recognition_id=request.recognition_id,
                paraphrases=paraphrases_response.paraphrases
            )
        )
        
        return response

    def get_paraphrases_by_recognition_id(self, recognition_id: str) -> List[str]:
        """recognition_id에 해당하는 paraphrase_content 목록을 반환합니다."""
        try:
            paraphrases_data = self.paraphrase_repo.get_paraphrases_by_recognition_id(recognition_id)
            return [p.get('paraphrase_content', '') for p in paraphrases_data]
        except Exception as e:
            logger.error(f"패러프레이즈 조회 중 오류 발생 (Recognition ID: {recognition_id}): {str(e)}", exc_info=True)
            return []

    def generate_recommended_context_tags(self, request: RecommendationRequest) -> BaseResponse[RecommendationResponse]:
        """
        사용자 컨텍스트와 내용을 기반으로 LLM이 추천한 컨텍스트 ID와 태그 ID 목록을 반환하고,
        각 추천 항목을 RecommendedContextTag 문서로 저장합니다.
        
        Args:
            request: 태그 추천 요청 정보를 담은 Pydantic 모델 (user_id, recognition_id, content 포함)
            
        Returns:
            추천된 컨텍스트 ID와 태그 ID 목록을 담은 응답 객체
        """
        try:
            user = self.user_use_case.create_user_instance(request.user_id)
            if not user:
                return BaseResponse[RecommendationResponse](
                    code=404, status="error", message="사용자 정보를 찾을 수 없습니다.", data=None)
            
            paraphrase_contents = self.get_paraphrases_by_recognition_id(request.recognition_id)
            if not paraphrase_contents:
                logger.warning(f"Recognition ID {request.recognition_id}에 대한 패러프레이즈를 찾을 수 없습니다.")
                return BaseResponse[RecommendationResponse](
                    code=404, 
                    status="error", 
                    message=f"Recognition ID {request.recognition_id}에 대한 패러프레이즈를 찾을 수 없습니다.", 
                    data=None
                )
            
            paraphrases_str = ", ".join(paraphrase_contents) if paraphrase_contents else ""
            
            formatted_contexts = self.context_use_case.get_formatted_user_contexts(request.user_id)
            formatted_tags = self.tag_use_case.get_formatted_user_tags(request.user_id)
            
            llm_response = self.ai_service.generate_context_tags(
                user_bio=user.bio_str,
                formatted_contexts=formatted_contexts,
                formatted_tags=formatted_tags,
                paraphrases_content=paraphrases_str,
                content=request.content
            )
            
            if not llm_response:
                 logger.error("LLM 호출 실패 또는 빈 결과")
                 return BaseResponse[RecommendationResponse](
                    code=500, status="error", message="LLM 호출 실패 또는 빈 결과", data=None)
            
            recognition_id = request.recognition_id
            created_recommendation_ids = []
            recommended_context_id = llm_response.recommended_context_id

            if recommended_context_id and llm_response.recommended_tag_ids:
                for tag_id in llm_response.recommended_tag_ids:
                    try:
                        created_id = self.recommended_repo.create_recommended_tags(
                            recognition_id=recognition_id,
                            user_context_id=recommended_context_id,
                            user_tag_id=tag_id
                        )
                        created_recommendation_ids.append(created_id)
                        logger.info(f"추천 저장 완료 (Context: {recommended_context_id}, Tag: {tag_id}, Recommendation ID: {created_id})")
                    except Exception as e:
                        logger.error(f"추천 저장 중 오류 발생 (Context: {recommended_context_id}, Tag: {tag_id}): {str(e)}", exc_info=True)
            elif recommended_context_id:
                 try:
                    created_id = self.recommended_repo.create_recommended_tags(
                        recognition_id=recognition_id,
                        user_context_id=recommended_context_id,
                        user_tag_id=None
                    )
                    created_recommendation_ids.append(created_id)
                    logger.info(f"컨텍스트 추천만 저장 완료 (Context ID: {recommended_context_id}, Recommendation ID: {created_id})")
                 except Exception as e:
                    logger.error(f"컨텍스트 추천 저장 중 오류 발생 (Context ID: {recommended_context_id}): {str(e)}", exc_info=True)
            elif llm_response.recommended_tag_ids:
                 logger.warning("Warning: 태그만 추천되고 컨텍스트 ID가 없습니다. 저장 로직 검토 필요.")
                 pass
            
            logger.info(f"생성된 추천 문서 ID 목록: {created_recommendation_ids}")
            if not created_recommendation_ids:
                logger.info("저장된 추천 문서가 없습니다.")

            final_response_data = RecommendationResponse(
                 recognition_id=recognition_id,
                 recommended_context_id=llm_response.recommended_context_id,
                 recommended_tag_ids=llm_response.recommended_tag_ids
            )
            
            return BaseResponse[RecommendationResponse](
                code=200,
                status="success",
                message="추천 context ID와 tag ID 목록 반환 성공",
                data=final_response_data
            )
        
        except Exception as e:
            logger.error(f"태그 추천 처리 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
            return BaseResponse[RecommendationResponse](
                code=500, status="error", message=f"태그 추천 처리 중 오류 발생: {str(e)}", data=None)

    def generate_temp_actionable_steps(self, request: TempActionableStepsRequest) -> BaseResponse[TempActionableStepsResponse]:
        """
        임시 액션 단계를 생성합니다.
        
        Args:
            request: 임시 액션 단계 생성 요청 정보를 담은 Pydantic 모델
            
        Returns:
            생성된 임시 액션 단계 목록을 담은 응답 객체
        """
        user = self.user_use_case.create_user_instance(request.user_id)
        if not user:
            return BaseResponse[TempActionableStepsResponse](
                code=404,
                status="error",
                message="사용자 정보를 찾을 수 없습니다.",
                data=None
            )
        
        formatted_contexts = self.context_use_case.get_formatted_user_contexts(request.user_id)
        formatted_tags = self.tag_use_case.get_formatted_user_tags(request.user_id)
        
        steps_response = self.ai_service.generate_temp_actionable_steps(
            user.bio_str,
            formatted_contexts,
            formatted_tags,    
            request.content
        )

        print(steps_response);
        for step in steps_response.actionable_steps:
            print(step);
        
        steps_response.recognition_id = request.recognition_id
        
        steps_data = []
        for step in steps_response.actionable_steps:
            step_data = {
                'recognition_id': request.recognition_id,
                'step_content': step.content,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            steps_data.append(step_data)
        
        self.temp_step_repo.create_multiple_temp_steps(steps_data)
        
        response = BaseResponse[TempActionableStepsResponse](
            code=200,
            status="success",
            message="임시 actionable steps 생성 성공",
            data=steps_response
        )
        return response