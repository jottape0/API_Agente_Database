from pydantic import BaseModel

class AskQueryResponse(BaseModel):
    answer: str