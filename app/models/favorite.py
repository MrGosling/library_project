from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Favorite(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey('books.id'), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
