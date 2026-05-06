from pydantic import BaseModel, ConfigDict


class GenreBase(BaseModel):
    name: str


class GenreCreate(GenreBase):
    pass


class GenreRead(GenreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
