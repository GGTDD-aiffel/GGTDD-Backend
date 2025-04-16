from typing import List, Optional
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

class ParaphraseResponse(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    paraphrases: List[str] = Field(default_factory=list, description="생성된 패러프레이즈 목록")

class RecommendationRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    content: str = Field(..., description="추천할 원본 텍스트 내용")
    user_id: str = Field(..., description="사용자 ID")

class RecommendationResponse(BaseModel):
    """LLM이 추천한 컨텍스트 ID와 태그 ID 목록을 담는 모델"""
    recognition_id: str = Field(..., description="인식 아이템 ID")
    recommended_context_id: Optional[str] = Field(None, description="추천된 컨텍스트 ID")
    recommended_tag_ids: List[str] = Field(default_factory=list, description="추천된 태그 ID 목록")

class TempActionableStepsRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    content: str = Field(..., description="추천할 원본 텍스트 내용")
    user_id: str = Field(..., description="사용자 ID")

class TempActionableStep(BaseModel):
    context: str = Field(..., description="추천된 컨텍스트")
    content: str = Field(..., description="추천된 내용")
    recommended_tag_ids: List[str] = Field(default_factory=list, description="추천된 태그 ID 목록")

class TempActionableStepsResponse(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    actionable_steps: List[TempActionableStep] = Field(default_factory=list, description="추천된 액션 스텝 목록")