from pydantic import BaseModel, Field


class BookForRecommendation(BaseModel):
    id: int | str | None = None
    title: str
    author: str | None = None
    genre: str | None = None
    description: str | None = None


class RecommendationRequest(BaseModel):
    read_books: list[BookForRecommendation] = Field(default_factory=list)
    catalog: list[BookForRecommendation] = Field(default_factory=list)
    limit: int = Field(default=5, ge=1, le=10)


class RecommendationItem(BaseModel):
    id: int | str | None = None
    title: str
    author: str | None = None
    reason: str


class RecommendationResponse(BaseModel):
    provider: str
    model: str
    recommendations: list[RecommendationItem]
