from pydantic import BaseModel


class ResetPasswordRequest(BaseModel):
    username: str
    password: str
    confirm_password: str