from pydantic import BaseModel


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: str | None = None


class GenreRead(GenreBase):
    id: int

    class Config:
        from_attributes = True
