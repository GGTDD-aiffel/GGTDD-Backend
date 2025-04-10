from app.infrastructure.repository.user_context_repository import UserContextRepository
from app.infrastructure.repository.user_tags_repository import UserTagRepository
from fastapi import APIRouter, Depends
from langchain_openai import ChatOpenAI

from app.infrastructure.LLMs.recognition_generator import RecognitionGenerator
from app.infrastructure.repository.paraphrase_repository import ParaphraseRepository
from app.infrastructure.repository.recommended_context_tags_repository import RecommendedContextTagsRepository
from app.infrastructure.repository.temp_acitonable_step_repository import TempActionableStepRepository
from app.infrastructure.repository.user_repository import UserRepository
from app.domain.user.use_cases import UserUseCase
from app.domain.user_tags.use_cases import UserTagUseCase
from app.domain.user_contexts.use_cases import UserContextUseCase
from app.domain.recognition.use_cases import RecognitionUseCase
from app.domain.recognition.models import (
    ParaphraseRequest,
    RecommendationRequest,
    TempActionableStepsRequest,
)
from app.infrastructure.LLMs.user_generator import UserGenerator

router = APIRouter()

# 전역 의존성 인스턴스
llm_model = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
user_repo = UserRepository()
tag_repo = UserTagRepository()
context_repo = UserContextRepository()
paraphrase_repo = ParaphraseRepository()
recommended_repo = RecommendedContextTagsRepository()
temp_step_repo = TempActionableStepRepository()

# 의존성 제공 함수들
def get_llm_model():
    return llm_model

def get_user_repo():
    return user_repo

def get_tag_repo():
    return tag_repo

def get_context_repo():
    return context_repo

def get_paraphrase_repo():
    return paraphrase_repo

def get_recommended_tags_repo():
    return recommended_repo

def get_temp_step_repo():
    return temp_step_repo

def get_recognition_generator(llm: ChatOpenAI = Depends(get_llm_model)):
    return RecognitionGenerator(llm)

def get_user_generator(llm: ChatOpenAI = Depends(get_llm_model)):
    return UserGenerator(llm)

def get_tag_use_case(repo: UserTagRepository = Depends(get_tag_repo)):
    return UserTagUseCase(repo)

def get_context_use_case(repo: UserContextRepository = Depends(get_context_repo)):
    return UserContextUseCase(repo)

def get_user_use_case(
    repo: UserRepository = Depends(get_user_repo),
    user_generator: UserGenerator = Depends(get_user_generator)
):
    return UserUseCase(
        repo=repo,
        llm_service=user_generator
    )

def get_recognition_use_case(
    ai_service: RecognitionGenerator = Depends(get_recognition_generator),
    paraphrase_repo: ParaphraseRepository = Depends(get_paraphrase_repo),
    recommended_repo: RecommendedContextTagsRepository = Depends(get_recommended_tags_repo),
    temp_step_repo: TempActionableStepRepository = Depends(get_temp_step_repo),
    user_use_case: UserUseCase = Depends(get_user_use_case),
    tag_use_case: UserTagUseCase = Depends(get_tag_use_case),
    context_use_case: UserContextUseCase = Depends(get_context_use_case)
):
    return RecognitionUseCase(
        ai_service=ai_service,
        paraphrase_repo=paraphrase_repo,
        recommended_repo=recommended_repo,
        temp_step_repo=temp_step_repo,
        user_use_case=user_use_case,
        tag_use_case=tag_use_case,
        context_use_case=context_use_case
    )

@router.post("/api/paraphrase")
def generate_paraphrase(
    request: ParaphraseRequest,
    use_case: RecognitionUseCase = Depends(get_recognition_use_case)
):
    return use_case.generate_paraphrase(request)

@router.post("/api/recommended/context_tags")
def generate_recommended_context_tags(
    request: RecommendationRequest,
    use_case: RecognitionUseCase = Depends(get_recognition_use_case)
):
    return use_case.generate_recommended_context_tags(request)

@router.post("/api/temp_actionable_steps")
def generate_temp_actionable_steps(
    request: TempActionableStepsRequest,
    use_case: RecognitionUseCase = Depends(get_recognition_use_case)
):
    return use_case.generate_temp_actionable_steps(request)

# @router.post("/api/actionable_steps/save")
# def save_actionable_steps(temp_step_ids: list[str], content_id: str):
#     use_case.save_actionable_steps(temp_step_ids, content_id)
#     return {"message": "Actionable steps saved"}