from fastapi import APIRouter

from app.infrastructure.firebase_repo import FirebaseRepository
from app.domain.user.use_cases import UserUseCase
from app.domain.user.models import User

router = APIRouter()
use_case = UserUseCase(FirebaseRepository())