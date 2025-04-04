from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI

from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.LLMs.user_generator import UserGenerator
from app.domain.user.use_cases import UserUseCase
from app.domain.user.models import User, UserRequest, UserPromptsResponse

router = APIRouter()

# 전역 의존성 인스턴스 (애플리케이션 수명 주기 동안 재사용)
firebase_repo = FirebaseRepository()
llm_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)

# 의존성 제공 함수들
def get_firebase_repo():
    return firebase_repo

def get_llm_model():
    return llm_model

def get_user_generator(llm: ChatOpenAI = Depends(get_llm_model)):
    return UserGenerator(llm)

def get_use_case(repo: FirebaseRepository = Depends(get_firebase_repo), 
                user_generator: UserGenerator = Depends(get_user_generator)):
    return UserUseCase(repo, user_generator)

# API 엔드포인트 정의
@router.post("/api/user/generate")
def generate_prompts_and_tags(request: UserRequest, user_generator: UserGenerator = Depends(get_user_generator)):
    """사용자 프롬프트 생성"""
    user_use_case = UserUseCase(
        repo=FirebaseRepository(),
        llm_service=user_generator
    )
    
    response = user_use_case.generate_user_prompts_and_tags(request.user_id)
    
    return response
