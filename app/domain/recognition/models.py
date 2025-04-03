from typing import List
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
    user_context: str = Field(..., description="사용자 컨텍스트 문자열")

class ParaphraseResponse(BaseModel):
    paraphrases: List[str] = Field(default_factory=list, description="생성된 패러프레이즈 목록")

class RecommendationRequest(BaseModel):
    recognition_id: str = Field(..., description="인식 아이템 ID")
    content: str = Field(..., description="추천할 원본 텍스트 내용")
    user_context: str = Field(..., description="사용자 컨텍스트 문자열")

class RecommendationResponse(BaseModel):
    recommended_tags: List[str] = Field(default_factory=list, description="추천된 태그 목록")