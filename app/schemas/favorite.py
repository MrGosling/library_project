from pydantic import BaseModel, ConfigDict


class FavoriteBase(BaseModel):
    user_id: int
    book_id: int
    is_read: bool = False


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteRead(FavoriteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
