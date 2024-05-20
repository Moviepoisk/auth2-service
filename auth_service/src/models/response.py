from pydantic import BaseModel


class ResponseModel(BaseModel):
    detail: str | None = None
