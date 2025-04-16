from app.infrastructure.repository.user_repository import UserRepository
from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI

from app.infrastructure.LLMs.user_generator import UserGenerator
from app.domain.user.use_cases import UserUseCase
from app.domain.user.models import UserRequest

router = APIRouter()

# 전역 의존성 인스턴스 (애플리케이션 수명 주기 동안 재사용)
user_repo = UserRepository()
llm_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)

# 의존성 제공 함수들
def get_user_repo():
    return user_repo

def get_llm_model():
    return llm_model

def get_user_generator(llm: ChatOpenAI = Depends(get_llm_model)):
    return UserGenerator(llm)

def get_use_case(
    repo: UserRepository = Depends(get_user_repo), 
    user_generator: UserGenerator = Depends(get_user_generator),
):
    return UserUseCase(
        repo=repo, 
        llm_service=user_generator,
    )

# API 엔드포인트 정의
@router.post("/api/user/generate")
def generate_user_prompts(
    request: UserRequest, 
    use_case: UserUseCase = Depends(get_use_case)
):
    """사용자 프롬프트 생성"""
    response = use_case.generate_user_prompts(request.user_id)
    return response
