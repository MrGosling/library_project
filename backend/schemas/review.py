from pydantic import BaseModel, ConfigDict


class ReviewBase(BaseModel):
    rating: int
    text: str | None = None
    book_id: int
    user_id: int


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
