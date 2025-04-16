from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    code: int
    status: str
    message: str
    data: Optional[T] = None
