from pydantic import BaseModel
from app.infrastructure.LLMs.base_LLM_processoor import BaseLLMProcessor
from app.domain.recognition.models import ParaphraseResponse, RecommendationResponse, TempActionableStepsResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser

class RecognitionGenerator(BaseLLMProcessor):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
    
    def generate_paraphrase(self, user_context: str, user_tags: str, content: str):
        """인식된 내용을 바탕으로 패러프레이즈 생성"""
        
        prompt = """
        다음은 사용자가 입력한 할 일입니다. 당신은 사용자가 의도한 할 일을 최대한 구체적으로 이해해야 합니다.
        사용자가 하고자 하는 일을 정확히 이해하기 위해 사용자의 입력을 다시 작성하여 3개 내외로 사용자에게 제시하세요.
        "도서관에 가기"라는 할 일이 주어졌다면, "도서관에서 공부하기", "도서관에서 책 빌리기" 등으로 다시 작성할 수 있습니다.
        
        사용자가 입력한 할 일을 이해할 때에는 사용자의 인적 정보와 하루 일과를 함께 고려하세요.
        각각의 답변은 사용자의 입력을 왜곡하지 않으면서도 다양한 방식으로 다시 작성해야 합니다.
        각각의 답변은 "---"로 구분하고, 답변 외의 부수적인 내용은 생략하세요.

        사용자가 입력한 할 일: {content}
        사용자의 인적 정보: {bio}
        사용자의 태그: {tags}
        지침: {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=ParaphraseResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser
        
        response = chain.invoke({
            "content": content,
            "bio": user_context,
            "tags": user_tags,
            "format_instruction": format_instruction
        })
        
        return response
    
    def generate_context_tags(self, user_bio: str, user_tags: str, content: str):
        """인식된 내용을 바탕으로 추천 태그 생성"""
        
        prompt = """
        다음은 사용자가 입력한 해야 할 일입니다. 이 할 일에 대해 부여할 수 있는 태그를 생성하세요.

        태그를 붙이는 목적은 할 일을 관리하기 위한 데이터베이스에 사용하기 위해서입니다.
        각각의 할 일은 사용자의 하루를 나타내는 여러 장면을 담은 태그와 함께 저장되고, 사용자가 처한 맥락과 상황을 표현하는 태그에 맞춰 할 일을 추천합니다.

        시간 태그에는 휴일 여부, 요일, 하루 중의 시간대 등의 정보를 포함하세요.
        공간 태그에는 사용자의 위치, 활동하는 장소 등의 정보를 포함하세요.
        기타 태그에는 시간과 공간 태그에 포함되지 않지만 할 일의 맥락과 상황을 검색하기에 좋은 정보를 포함하세요.
        각각의 태그는 되도록이면 사용자의 인적 정보에 포함되어 있는 태그 정보를 활용하여 작성하세요.
        
        사용자가 입력한 할 일: {content}
        사용자의 인적 정보: {bio}
        사용자의 태그: {tags}
        지침: {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=RecommendationResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser
        
        response = chain.invoke({
            "content": content,
            "bio": user_bio,
            "tags": user_tags,
            "format_instruction": format_instruction
        })
        
        return response
    
    def generate_temp_actionable_steps(self, user_bio: str, user_tags: str, context: str, content: str):
        """사용자가 입력한 할 일을 actionable_steps로 분해 및 구체화"""
                
        prompt = """
        다음은 사용자가 입력한 해야 할 일입니다. 이 할 일에 대한 구체적인 스텝을 주어진 숫자에 맞추어 작성하세요.
        단, 생성할 스텝의 수가 0으로 주어진다면 스텝을 생성하지 않고, 태스크만 생성합니다.
        스텝에만 존재하는 필드를 태스크에 생성하지 않도록 주의하세요.

        Context는 사용자의 하루에 비추어 해당하는 할 일을 수행하는 맥락을 나타냅니다.
        시간 태그에는 휴일 여부, 요일, 하루 중의 시간대 등의 정보를 포함하세요.
        공간 태그에는 사용자의 위치, 활동하는 장소 등의 정보를 포함하세요.
        기타 태그에는 시간과 공간 태그에 포함되지 않지만 할 일의 맥락과 상황을 검색하기에 좋은 정보를 포함하세요.
        각각의 태그는 되도록이면 사용자의 인적 정보에 포함되어 있는 태그 정보를 활용하여 작성하세요.
        
        스텝을 생성할 때에는, 각 스텝을 수행하는 데에 필요한 노력과 시간을 고려하세요.

        사용자의 인적 정보: {bio}
        사용자의 맥락: {context}
        사용자의 하루 일과: {tags}
        사용자가 입력한 할 일: {content}
        지침: {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=TempActionableStepsResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser
        
        print(user_tags)

        response = chain.invoke({
            "bio": user_bio,
            "context": context,
            "tags": user_tags,
            "content": content,
            "format_instruction": format_instruction
        })
        
        return response
        

    def _create_prompt_template(self, prompt: str):
        """프롬프트 템플릿 생성"""
        return ChatPromptTemplate.from_template(prompt)
    
    def _get_format_instructions(self, outputParser: BaseOutputParser) -> str:
        """출력 형식 지침 생성"""
        return outputParser.get_format_instructions()
