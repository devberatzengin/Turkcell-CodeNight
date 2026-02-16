from pydantic import BaseModel


class UserSchema(BaseModel):
    user_id: str
    name: str
    city: str | None = None
    segment: str | None = None

    class Config:
        orm_mode = True
