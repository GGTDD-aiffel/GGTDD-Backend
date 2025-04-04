from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    code: int
    status: str
    message: str
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True