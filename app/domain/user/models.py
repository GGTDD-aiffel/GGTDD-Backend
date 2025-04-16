from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

class User(BaseModel):
    name: str = "알 수 없음"
    status: str = ""
    is_admin: bool = False
    is_premium: bool = False
    email: str = ""
    residence: str = ""
    birth_date: Optional[datetime] = None
    occupation: str = "알 수 없음"
    personality: list[str] = Field(default_factory=list)
    user_prompts: str = ""
        
    @property
    def bio_str(self):
        try:
            birth_date_str = self.birth_date.strftime('%Y-%m-%d') if self.birth_date else 'None'
            
            return_string = f"""
                                User:
                                    이름: {self.name}
                                    거주지: {self.residence}
                                    생년월일: {birth_date_str}
                                    직업: {self.occupation}
                                    성격: {', '.join(self.personality) if self.personality else '[]'}
                                    프롬프트 내용: {self.user_prompts if self.user_prompts else '없음'}
                            """
            return return_string
        except Exception as e:
            logger.error(f"bio_str 생성 중 오류 발생: {str(e)}", exc_info=True)
            
            return f"User: 이름: {self.name}, 직업: {self.occupation}"

    @property
    def metadata_str(self):
        return f"{self.name}_{self.status}, isAdmin: {self.is_admin}"

class UserRequest(BaseModel):
    user_id: str = Field(..., description="사용자 ID")

class UserPromptsResponse(BaseModel):
    prompts: list[str] = Field(default_factory=list, description="생성된 프롬프트 목록")