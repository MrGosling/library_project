from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class Review(Base):
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey('book.id', ondelete='CASCADE'), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'book_id', name='unique_user_book_review'),
    )

    # Relationships
    book: Mapped['Book'] = relationship(passive_deletes=True)
    user: Mapped['User'] = relationship(passive_deletes=True)
