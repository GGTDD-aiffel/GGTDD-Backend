from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    name: str
    status: str
    is_admin: bool
    email: str
    residence: str
    birth_date: Optional[datetime] = None
    occupation: str
    personality: list[str]
    location_tags: list[str] = []
    time_tags: list[str] = []
    other_tags: list[str] = []
    _prompts: list[str] = []
    selected_prompt: str = None
        
    @property
    def bio_str(self):
        birth_date_str = self.birth_date.strftime('%Y-%m-%d') if self.birth_date else 'None'
        prompts = '\n\t'.join(self._prompts) if self._prompts else '[]'
        
        return_string = f"""
User:
    이름: {self.name}
    거주지: {self.residence}
    생년월일: {birth_date_str}
    직업: {self.occupation}
    성격: {', '.join(self.personality) if self.personality else '[]'}
    장소 태그: {', '.join(self.location_tags) if self.location_tags else '[]'}
    시간 태그: {', '.join(self.time_tags) if self.time_tags else '[]'}
    기타 태그: {', '.join(self.other_tags) if self.other_tags else '[]'}
    프롬프트 수: {len(self._prompts)}
    프롬프트 내용: \n\t{prompts}
        """
        
        return return_string

    @property
    def metadata_str(self):
        return f"{self.name}_{self.status}, isAdmin: {self.is_admin}"