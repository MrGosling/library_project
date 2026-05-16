from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Review(Base):
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey('books.id'), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
