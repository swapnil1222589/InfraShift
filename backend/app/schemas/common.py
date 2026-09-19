
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    requestId: str | None = None
