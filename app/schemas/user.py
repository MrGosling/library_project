from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True
