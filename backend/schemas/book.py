from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    """Базовая схема книги."""

    title: str
    pub_year: int
    author_id: int
    description: str | None = None


class BookCreate(BookBase):
    """Схема создания книги."""

    pass


class BookUpdate(BaseModel):
    """Схема частичного обновления книги."""

    title: str | None = None
    pub_year: int | None = None
    author_id: int | None = None
    description: str | None = None


class BookRead(BookBase):
    """Схема чтения книги."""

    id: int

    model_config = ConfigDict(from_attributes=True)
