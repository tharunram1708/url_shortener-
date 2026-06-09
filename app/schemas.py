from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(..., min_length=6)
    role_name: Literal["user", "admin"] = "user"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role_name: str


class UrlCreateRequest(BaseModel):
    original_url: HttpUrl
    custom_code: str | None = Field(default=None, min_length=3, max_length=30)


class UrlUpdateRequest(BaseModel):
    original_url: HttpUrl | None = None
    short_code: str | None = Field(default=None, min_length=3, max_length=30)


class UrlResponse(BaseModel):
    id: int
    original_url: str
    short_code: str
    click_count: int
    created_by: int
    created_at: datetime
    last_accessed_at: datetime | None


class PaginatedUrls(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[UrlResponse]


class UrlAnalyticsResponse(BaseModel):
    short_code: str
    total_clicks: int
    created_at: datetime
    last_accessed_at: datetime | None


class AnalyticsSummaryResponse(BaseModel):
    total_urls: int
    total_clicks: int
    most_visited_url: UrlResponse | None
