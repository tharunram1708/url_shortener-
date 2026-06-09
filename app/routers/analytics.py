from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl, User
from app.schemas import AnalyticsSummaryResponse, UrlAnalyticsResponse
from app.security import get_current_user
from app.url_helpers import get_last_accessed_at, get_owned_url_or_404, to_url_response


router = APIRouter(tags=["Analytics"])


@router.get("/urls/{short_code}/analytics", response_model=UrlAnalyticsResponse)
def get_url_analytics(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    short_url = get_owned_url_or_404(db, short_code, current_user)
    return UrlAnalyticsResponse(
        short_code=short_url.short_code,
        total_clicks=short_url.click_count,
        created_at=short_url.created_at,
        last_accessed_at=get_last_accessed_at(db, short_url.id),
    )


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    view_all: bool = Query(default=False, description="Admins can include every user's URLs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ShortUrl)
    if current_user.role.role_name != "admin" or not view_all:
        query = query.filter(ShortUrl.created_by == current_user.id)

    total_urls = query.count()
    total_clicks = query.with_entities(func.coalesce(func.sum(ShortUrl.click_count), 0)).scalar()
    most_visited = query.order_by(ShortUrl.click_count.desc(), ShortUrl.created_at.asc()).first()

    return AnalyticsSummaryResponse(
        total_urls=total_urls,
        total_clicks=total_clicks,
        most_visited_url=to_url_response(db, most_visited) if most_visited else None,
    )
