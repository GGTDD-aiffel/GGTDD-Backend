from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.infrastructure.firebase_repo import FirebaseRepository
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
        paraphrases_response = self.ai_service.generate_paraphrase(
            self.get_user_context(request.user_id), 
            self.get_user_tags(request.user_id),
            request.content
        )
        
        for paraphrase in paraphrases_response.paraphrases:
            paraphrase_data = {
                'recognition_id': request.recognition_id,
                'paraphrase_content': paraphrase,
                'is_selected_paraphrase': False,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            # Save each paraphrase to the database
            self.repo.create_paraphrase(paraphrase_data)
        
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

    def generate_recommended_context_tags(self, request: RecommendationRequest) -> BaseResponse[RecommendationResponse]:
        """
        사용자 컨텍스트와 내용을 기반으로 태그를 추천하고 해당 태그의 ID를 가져옵니다.
        
        Args:
            request: 태그 추천 요청 정보를 담은 Pydantic 모델
            
        Returns:
            추천된 컨텍스트와 태그를 담은 응답 객체
        """
        try:
            # LLM으로 태그 생성
            recommendation_response = self.ai_service.generate_context_tags(
                self.get_user_context(request.user_id),
                self.get_user_tags(request.user_id),
                request.content
            )
            
            # 인식 ID 설정
            recommendation_response.recognition_id = request.recognition_id
            
            # 태그 ID 처리를 위한 헬퍼 함수
            def get_tag_ids(tag_list, tag_type):
                tag_ids = []
                created_tags = []
                
                for tag in tag_list:
                    # 기존 태그 ID 조회
                    tag_id = self.repo.get_user_tag_id(request.user_id, tag)
                    
                    # 태그가 없으면 생성
                    # if not tag_id:
                    #     tag_data = {
                    #         'user_id': request.user_id,
                    #         'tag_name': tag,
                    #         'tag_type': tag_type,
                    #         'created_at': firestore.SERVER_TIMESTAMP
                    #     }
                    #     tag_id = self.repo.create_user_tag(tag_data)
                    #     created_tags.append(tag)
                    
                    tag_ids.append(tag_id)
                
                # 새로 생성된 태그가 있으면 로깅
                if created_tags:
                    print(f"새로 생성된 {tag_type} 태그: {', '.join(created_tags)}")
                    
                return tag_ids
            
            # 각 태그 유형별로 ID 조회/생성
            recommendation_response.location_tags_ID = get_tag_ids(
                recommendation_response.location_tags_ID, "location")
            recommendation_response.time_tags_ID = get_tag_ids(
                recommendation_response.time_tags_ID, "time")
            recommendation_response.other_tags_ID = get_tag_ids(
                recommendation_response.other_tags_ID, "other")
            
            # 인식 객체에 태그 연결 정보 저장
            # tag_link_data = {
            #     'recognition_id': request.recognition_id,
            #     'location_tag_ids': recommendation_response.location_tags_ID,
            #     'time_tag_ids': recommendation_response.time_tags_ID,
            #     'other_tag_ids': recommendation_response.other_tags_ID,
            #     'updated_at': firestore.SERVER_TIMESTAMP
            # }
            # self.repo.update_recognition_tags(tag_link_data)
            
            return BaseResponse[RecommendationResponse](
                code=200,
                status="success",
                message="추천 context와 tags 반환 성공",
                data=recommendation_response
            )
        
        except Exception as e:
            print(f"태그 추천 중 오류 발생: {str(e)}")
            return BaseResponse[RecommendationResponse](
                code=500,
                status="error",
                message=f"태그 추천 중 오류 발생: {str(e)}",
                data=None
            )

    def generate_temp_actionable_steps(self, request: TempActionableStepsRequest) -> BaseResponse[TempActionableStepsResponse]:
        steps = self.ai_service.generate_temp_actionable_steps(
            self.get_user_context(request.user_id),
            self.get_user_tags(request.user_id),
            request.content
        )
        
        steps.recognition_id = request.recognition_id

        # for step in steps:
        #     temp_step_data = {
        #         'recognition_id': request.recognition_id,
        #         'step_content': step,
        #         'created_at': firestore.SERVER_TIMESTAMP
        #     }
        #     self.repo.create_temp_actionable_step(temp_step_data)
            
        response = BaseResponse[TempActionableStepsResponse](
            code=200,
            status="success",
            message="임시 actionable steps 생성 성공",
            data=steps
        )
        return response
    
    # def save_actionable_steps(self, temp_step_ids: list[str], content_id: str):
    #     for temp_id in temp_step_ids:
    #         temp_step = self.repo.get_temp_actionable_step(temp_id)
    #         if temp_step:
    #             actionable_step_data = {
    #                 'content_id': content_id,
    #                 'step_content': temp_step['step_content'],
    #                 'is_completed': False,
    #                 'created_at': firestore.SERVER_TIMESTAMP,
    #                 'updated_at': None
    #             }
    #             self.repo.create_actionable_step(actionable_step_data)

    def get_user_tags(self, user_id: str) -> List[str]:
        """
        사용자의 태그를 데이터베이스에서 가져옵니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            사용자 태그 목록
        """
        tags = self.repo.get_user_tags(user_id)
        return [tag['tag_name'] for tag in tags] if tags else []
    
    def get_user_context(self, user_id: str) -> dict:
        """_summary_
        사용자의 컨텍스트를 데이터베이스에서 가져옵니다.

        Args:
            user_id (str): 사용자 ID

        Returns:
            List[str]: 사용자 컨텍스트 목록
        """
        contexts = self.repo.get_user_prompts(user_id)
        return [context['context_name'] for context in contexts] if contexts else []