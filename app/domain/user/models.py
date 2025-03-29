from pydantic import BaseModel
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.infrastructure.LLMs.UserGenerator import UserGenerator

class UserPromptsTemplate(BaseModel):
    location_tags: list[str] = []
    time_tags: list[str] = []
    other_tags: list[str] = []
    prompt: list[str] = []

class User:
    def __init__(self, name, uid, status, is_admin, email, residence, birth_date, occupation, personality):
        self.name = name
        self.uid = uid
        self.status = status
        self.is_admin = is_admin
        self.email = email
        self.residence = residence
        self.birth_date = birth_date
        self.occupation = occupation
        self.personality = personality
        self.location_tags = []
        self.time_tags = []
        self.other_tags = []
        self._prompts = []
        
    def __str__(self):
        birth_date_str = self.birth_date.strftime('%Y-%m-%d') if self.birth_date else 'None'
        prompts = '\n\t'.join(self._prompts) if self._prompts else '[]'
        
        return f"""User:
        이름: {self.name}
        거주지: {self.residence}
        생년월일: {birth_date_str}
        직업: {self.occupation}
        성격: {', '.join(self.personality) if self.personality else '[]'}
        장소 태그: {', '.join(self.location_tags) if self.location_tags else '[]'}
        시간 태그: {', '.join(self.time_tags) if self.time_tags else '[]'}
        기타 태그: {', '.join(self.other_tags) if self.other_tags else '[]'}
        프롬프트 수: {len(self._prompts)}
        프롬프트 내용: {prompts}
        """
        
    @property
    def metadata_str(self):
        return f"{self.name}_{self.uid}_{self.status}, isAdmin: {self.is_admin}"
        
    
    def generate_prompts(self, llm_service: UserGenerator):
        """사용자 정보 기반 프롬프트 생성"""
        prompt_template = self._create_prompt_template()
        output_parser = PydanticOutputParser(pydantic_object=UserPromptsTemplate)
        format_instruction = self._get_format_instructions()
        
        chain = prompt_template | llm_service.llm | output_parser
        
        response = chain.invoke({
            "bio": self, "format_instruction": format_instruction
        })
        
        self._prompts = response.prompt
        return self._prompts
    
    def _create_prompt_template(self):
        """프롬프트 템플릿 생성"""
        return ChatPromptTemplate.from_template("""
        다음은 사용자 정보입니다. 이 정보를 바탕으로, 사용자의 성격과 하루 일과, 주요 관심사를를 상상해서 1문단으로 작성하세요.
        이를 작성하는 이유는 사용자의 할 일을 사용자의 생활패턴과 맥락에 맞게 구체화하여 추천하기 위해서입니다.
        사용자에 대한 이해가 깊어질수록 사용자에게 더 유용한 할 일을 추천할 수 있습니다.
        사용자의 긍정적인 면과 부정적인 면을 모두 포함할 수 있도록 작성하세요.

        작성된 내용 중 사용자가 적합한 것을 선택할 수 있도록, 서로 다른 내용의 답변을 3~5개 생성하세요.
        각각의 답변은 사용자 정보의 다른 부분에 집중하며, 서로 비슷하지 않은 내용이어야 합니다.
        예를 들어 한 답변이 "대중교통"이라는 키워드에 집중한다면, 다른 답변은 "도서관" 등 다른 맥락에 집중할 수 있습니다.
        그러나 모든 답변은 사용자의 전반적인 일상을 구성할 수 있어야 합니다.
        만약 비슷한 답변이 생성된다면 생략하세요.
        
        사용자 정보: {bio}
        답변 지침: {format_instruction}
        """)
    
    def _get_format_instructions(self):
        """출력 형식 지침 생성"""
        output_parser = PydanticOutputParser(pydantic_object=UserPromptsTemplate)
        return output_parser.get_format_instructions()
    
    def select_prompt(self, prompt_index):
        """특정 프롬프트 선택"""
        if 0 <= prompt_index < len(self._prompts):
            self.selected_prompt = self._prompts[prompt_index]
            return self.selected_prompt
        raise ValueError("유효하지 않은 프롬프트 인덱스입니다")
    
    def generate_tags_from_prompt(self, llm_service):
        """선택된 프롬프트에서 태그 추출"""
        if not hasattr(self, 'selected_prompt'):
            raise ValueError("먼저 프롬프트를 선택해야 합니다")
            
        tags = llm_service.extract_tags(self.selected_prompt)
        self.location_tags = tags.get('location', [])
        self.time_tags = tags.get('time', [])
        self.other_tags = tags.get('other', [])
        return tags