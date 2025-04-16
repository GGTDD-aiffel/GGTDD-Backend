from pydantic import BaseModel
from app.infrastructure.LLMs.base_LLM_processoor import BaseLLMProcessor
from app.domain.recognition.models import ParaphraseResponse, RecommendationResponse, TempActionableStepsResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser

class RecognitionGenerator(BaseLLMProcessor):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
    
    def generate_paraphrase(self, user_bio: str, user_contexts: str, user_tags: str, content: str):
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
        사용자의 맥락 (콤마로 구분): {contexts}
        사용자의 태그 (콤마로 구분): {tags}
        
        아래 맥락과 태그는 콤마(,)로 구분된 목록으로 제공됩니다. 각 항목을 개별적으로 고려하여 사용자의 할 일을 더 정확하게 이해하세요.
        만약 특정 맥락이나 태그가 사용자의 할 일과 관련이 있다면, 그 맥락과 태그를 활용하여 보다 구체적인 패러프레이즈를 생성하세요.
        지침: {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=ParaphraseResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser
        
        response = chain.invoke({
            "content": content,
            "bio": user_bio,
            "contexts": user_contexts,
            "tags": user_tags,
            "format_instruction": format_instruction
        })
        
        return response
    
    def generate_context_tags(self, user_bio: str, formatted_contexts: str, formatted_tags: str, paraphrases_content: str, content: str) -> RecommendationResponse:
        """인식된 내용을 바탕으로 추천 컨텍스트 ID와 태그 ID 목록을 생성합니다.
        
        Args:
            user_bio: 사용자 바이오 정보 문자열
            formatted_contexts: 'ID: 이름' 형식의 사용자 컨텍스트 문자열
            formatted_tags: 'ID: 이름(타입)' 형식의 사용자 태그 문자열 (예: id1: 집(space), id2: 주말(time), id3: 프로젝트(other))
            paraphrases_content: 콤마로 구분된 패러프레이즈 문자열
            content: 사용자가 입력한 원본 내용
            
        Returns:
            추천된 컨텍스트 ID 1개와 태그 ID 목록을 포함하는 RecommendationResponse 모델
        """
        
        prompt = """
        다음 정보들을 바탕으로 사용자가 입력한 할 일과 가장 관련성이 높은 **컨텍스트 ID 1개**와 **태그 ID 여러 개**를 추천해주세요.
        추천은 반드시 아래 제공된 사용자의 기존 컨텍스트 및 태그 목록 내에서만 이루어져야 합니다.

        입력 정보:
        1. 사용자가 입력한 원본 내용: {content}
        2. 사용자의 의도를 파악하기 위해 생성된 패러프레이즈들 (콤마로 구분): {paraphrases}
        3. 사용자 정보 (Bio): {bio}
        4. 사용자가 이미 정의한 컨텍스트 목록 (형식: ID: 이름): {contexts}
        5. 사용자가 이미 정의한 태그 목록 (형식: ID: 이름(타입)): {tags}
           - 태그 타입 예시: space(장소 관련), time(시간 관련), other(기타) 등 (향후 다른 타입이 추가될 수 있음)

        출력 지침:
        - **가장 중요:** 사용자의 기존 컨텍스트 목록({contexts}) 중에서 할 일과 가장 관련성이 높은 것의 **ID 1개를 반드시 선택하세요.** 관련성이 조금 낮더라도 가장 가능성 있는 ID 하나를 선택해야 합니다. `recommended_context_id` 필드는 null이 되어서는 안 됩니다.
        
        - **태그 추천 (매우 중요):** 사용자의 기존 태그 목록({tags}) 중에서 **최소 2개, 최대 5개**의 태그 ID를 선택하세요. 강한 관련성이 없더라도 약간이라도 관련된 태그는 모두 포함하세요. 
        
        - 태그 선택 시 다음을 고려하세요:
          * 장소(location) 관련 태그 최소 1개
          * 시간(time) 관련 태그 최소 1개
          * 기타(other) 태그 중 관련 있는 것
          * 직접적인 관련성 외에도 간접적인 연관성이 있는 태그도 포함하세요
        
        - 예를 들어, "도서관에서 책 읽기"라는 할 일의 경우:
          * location 태그: "도서관", "학교" 등 장소 관련 태그 (포함 가능한 모든 관련 장소)
          * time 태그: "오후", "주말", "자유시간" 등 가능한 시간 관련 태그
          * other 태그: "공부", "취미", "독서" 등 활동과 관련된 태그
        
        - 반드시 아래 JSON 형식에 맞춰 ID만 포함하여 출력하세요:
        
        {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=RecommendationResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser
        
        response = chain.invoke({
            "content": content,
            "paraphrases": paraphrases_content,
            "bio": user_bio,
            "contexts": formatted_contexts,
            "tags": formatted_tags,
            "format_instruction": format_instruction
        })
        
        return response
    
    def generate_temp_actionable_steps(self, user_bio: str, formatted_contexts: str, formatted_tags: str, content: str):
        """사용자의 할 일을 바탕으로 실행 가능한 단계를 생성"""
        
        prompt = """
        당신은 사용자가 입력한 할 일을 바탕으로 실행 가능한 단계(actionable steps)를 구체적으로 제시하는 역할을 맡고 있습니다.
        
        사용자의 할 일: {content}
        
        사용자의 정보: {bio}
        
        사용자의 컨텍스트 목록(콤마로 구분): 
        {contexts}
        
        사용자의 태그 목록(콤마로 구분): 
        {tags}
        
        위 정보는 "ID: 이름" 또는 "ID: 이름(타입)" 형식으로 콤마(,)로 구분되어 있습니다.
        각 항목의 ID를 참조하여 응답해야 합니다.
        
        할 일과 관련된 컨텍스트와 태그를 고려하여, 실행 가능한 구체적인 단계를 최소 2개에서 최대 5개까지 제시해주세요.
        각 단계는 다음 요소를 포함해야 합니다:
        
        1. context: 해당 단계를 수행할 컨텍스트(장소나 상황)의 ID - 반드시 사용자 컨텍스트 목록에서 제공된 ID만 사용하세요.
        
        2. content: 구체적으로 수행할 행동에 대한 설명
        
        3. recommended_tag_ids: 해당 단계와 관련된 태그 ID 목록 - 반드시 제공된 태그 목록에서 ID만 선택하세요.
        
        태그 선택 시 다음을 고려하세요:
        - 각 단계마다 최소 2개, 최대 5개의 태그 ID를 선택하세요.
        - 다양한 타입(location, time, other)의 태그를 골고루 포함하세요.
        - 관련성이 높지 않더라도 약간이라도 관련된 태그는 모두 포함하세요.
        - 직접적인 관련성 외에도 간접적인 연관성이 있는 태그도 포함하세요.
        
        중요: 생성한 모든 단계에 대해 반드시 ID만 포함하여 출력하세요. 이름이나 설명을 ID 필드에 포함하지 마세요.
        
        예를 들어, 컨텍스트 목록에 "abc123: 집"이 있다면, context 필드에는 "abc123"만 포함해야 합니다.
        태그 목록에 "xyz789: 저녁(time)", "def456: 주방(location)"이 있다면, recommended_tag_ids 필드에는 ["xyz789", "def456"]과 같이 ID만 포함해야 합니다.
        
        응답 형식:
        {format_instruction}
        """
        
        prompt_template = self._create_prompt_template(prompt)
        output_parser = PydanticOutputParser(pydantic_object=TempActionableStepsResponse)
        format_instruction = self._get_format_instructions(output_parser)
        
        chain = prompt_template | self.llm | output_parser

        response = chain.invoke({
            "content": content,
            "bio": user_bio,
            "contexts": formatted_contexts,
            "tags": formatted_tags,
            "format_instruction": format_instruction
        })
        
        return response
        

    def _create_prompt_template(self, prompt: str):
        """프롬프트 템플릿 생성"""
        return ChatPromptTemplate.from_template(prompt)
    
    def _get_format_instructions(self, outputParser: BaseOutputParser) -> str:
        """출력 형식 지침 생성"""
        return outputParser.get_format_instructions()
