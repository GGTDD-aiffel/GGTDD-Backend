from .BaseLLMProcessor import BaseLLMProcessor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from typing import Optional, Dict, Any, List
import json

class UserGenerator(BaseLLMProcessor):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)