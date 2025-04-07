from typing import List, Dict, Any, ClassVar
from pydantic import BaseModel, Field

class Paraphrase(BaseModel):
    paraphrase_id: str
    recognition_id: str
    paraphrase_content: str
    is_selected_paraphrase: bool
    created_at: str

class ParaphraseRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    content: str = Field(..., description="패러프레이즈할 원본 텍스트 내용")
    user_id: str = Field(..., description="사용자 ID")
    user_context: str = Field(..., description="사용자 컨텍스트 문자열")

class ParaphraseResponse(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    paraphrases: List[str] = Field(default_factory=list, description="생성된 패러프레이즈 목록")

class RecommendationRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    content: str = Field(..., description="추천할 원본 텍스트 내용")
    user_id: str = Field(..., description="사용자 ID")

class RecommendationResponse(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    context: str = Field(..., description="추천된 컨텍스트")
    location_tags_ID: List[str] = Field(default_factory=list, description="추천된 위치 태그 목록")
    time_tags_ID: List[str] = Field(default_factory=list, description="추천된 시간 태그 목록")
    other_tags_ID: List[str] = Field(default_factory=list, description="추천된 기타 태그 목록")
    
class TempActionableStepsRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    recommended_context: Dict[str, str] = Field(
        default_factory=dict, 
        description="컨텍스트 키와 이름으로 구성된 딕셔너리 (예: {'39hmTZZxqIEAsJsD4Kwh': 'purpose_transit'})"
    )
    recommended_tags: Dict[str, str] = Field(
        default_factory=dict, 
        description="태그 키와 이름으로 구성된 딕셔너리 (예: {'7FTZ0Syq7yUnDS8gte1o': '집안일'})"
    )
    content: str = Field(..., description="추천할 원본 텍스트 내용")
    user_id: str = Field(..., description="사용자 ID")

class TempActionableStep(BaseModel):
    context: str = Field(..., description="추천된 컨텍스트")
    content: str = Field(..., description="추천된 내용")
    location_tags_ID: List[str] = Field(default_factory=list, description="추천된 위치 태그 목록")
    time_tags_ID: List[str] = Field(default_factory=list, description="추천된 시간 태그 목록")
    other_tags_ID: List[str] = Field(default_factory=list, description="추천된 기타 태그 목록")

class TempActionableStepsResponse(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    actionable_steps: List[TempActionableStep] = Field(default_factory=list, description="추천된 액션 스텝 목록")
    
    model_config: ClassVar[Dict[str, Any]] = {
        "json_schema_extra": {
            "examples": [
                {
                    "recognition_id": "abc123",
                    "actionable_steps": [
                        {
                            "context": "work",
                            "content": "이메일 확인하기",
                            "location_tags_ID": ["office"],
                            "time_tags_ID": ["morning"],
                            "other_tags_ID": ["urgent"]
                        }
                    ]
                }
            ]
        }
    }