from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Book(Base):
    """SQLAlchemy-модель книги в библиотечном каталоге."""

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    pub_year: Mapped[int] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('authors.id'), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
