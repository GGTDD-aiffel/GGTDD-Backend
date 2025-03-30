from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.infrastructure.LLMs.base_LLM_processoor import BaseLLMProcessor
from app.domain.user.models import User

class UserGenerator(BaseLLMProcessor):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)

    def generate_prompts(self, user: User):
        """사용자 정보 기반 프롬프트 생성"""
        prompt_template = self._create_prompt_template()
        output_parser = PydanticOutputParser(pydantic_object=UserPromptsTemplate)
        format_instruction = self._get_format_instructions()
        
        chain = prompt_template | self.llm | output_parser
        
        response = chain.invoke({
            "bio": user.bio_str, "format_instruction": format_instruction
        })
        
        user._prompts = response.prompt
        return user._prompts
    
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

class UserPromptsTemplate(BaseModel):
    prompt: list[str] = []
