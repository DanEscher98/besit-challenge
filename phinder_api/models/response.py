from datetime import datetime
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIError(BaseModel):
    message: str
    status: int


class APIResponse(BaseModel, Generic[T]):
    success: bool
    timestamp: str = datetime.now().isoformat()
    data: Optional[T] = None
    error: Optional[APIError] = None

    @classmethod
    def ok(cls, data: T):
        return cls(success=True, data=data, timestamp=datetime.now().isoformat())

    @classmethod
    def fail(cls, message: str, http_status: int):
        return cls(
            success=False,
            error=APIError(message=message, status=http_status),
            timestamp=datetime.now().isoformat(),
        )
