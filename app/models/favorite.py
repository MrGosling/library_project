from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class Favorite(Base):
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey('book.id', ondelete='CASCADE'), nullable=False
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user: Mapped['User'] = relationship()
    book: Mapped['Book'] = relationship()
