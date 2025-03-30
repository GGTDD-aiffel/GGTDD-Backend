from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI

from app.infrastructure.firebase_repo import FirebaseRepository
from app.infrastructure.LLMs.user_generator import UserGenerator
from app.domain.user.use_cases import UserUseCase
from app.domain.user.models import User

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
def generate_user(user_id: str, use_case: UserUseCase = Depends(get_use_case)):
    """사용자 정보 생성"""
    return use_case.create_user(user_id)

@router.post("/api/user/prompt/generate")
def generate_prompts(user: User, user_generator: UserGenerator = Depends(get_user_generator)):
    """사용자 프롬프트 생성"""
    return user_generator.generate_prompts(user)

@router.post("/api/user/prompt/select")
def select_prompt(user: User, index: int, use_case: UserUseCase = Depends(get_use_case)):
    """사용자 프롬프트 선택"""
    return use_case.select_prompt(user, index)

@router.post("/api/user/tag/update")
def update_tags(user: User, use_case: UserUseCase = Depends(get_use_case)):
    """사용자 태그 업데이트"""
    return use_case.update_tags(user)
