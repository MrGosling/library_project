from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db import Base

if TYPE_CHECKING:
    from backend.models.author import Author
    from backend.models.category import Category
    from backend.models.genre import Genre


book_genre = Table(
    'book_genre',
    Base.metadata,
    Column(
        'book_id', ForeignKey('book.id', ondelete='CASCADE'), primary_key=True
    ),
    Column(
        'genre_id',
        ForeignKey('genre.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)

book_category = Table(
    'book_category',
    Base.metadata,
    Column(
        'book_id', ForeignKey('book.id', ondelete='CASCADE'), primary_key=True
    ),
    Column(
        'category_id',
        ForeignKey('category.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Book(Base):
    """SQLAlchemy-модель книги в библиотечном каталоге."""

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    pub_year: Mapped[int] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('author.id', ondelete='CASCADE'), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    author: Mapped['Author'] = relationship(back_populates='books')
    genres: Mapped[List['Genre']] = relationship(
        secondary=book_genre, back_populates='books'
    )
    categories: Mapped[List['Category']] = relationship(
        secondary=book_category, back_populates='books'
    )
