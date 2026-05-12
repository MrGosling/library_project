from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    pub_year: int
    author_id: int
    description: str | None = None


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

