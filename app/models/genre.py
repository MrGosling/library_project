from typing import TYPE_CHECKING, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.book import Book, book_genre


class Genre(Base):
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    books: Mapped[List['Book']] = relationship(
        secondary='book_genre', back_populates='genres'
    )
