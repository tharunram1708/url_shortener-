from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl, User
from app.schemas import PaginatedUrls
from app.security import require_admin
from app.url_helpers import to_url_response


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/urls", response_model=PaginatedUrls)
def admin_list_all_urls(
    original_url: str | None = Query(default=None),
    short_code: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(ShortUrl)
    if original_url:
        query = query.filter(ShortUrl.original_url.ilike(f"%{original_url.strip()}%"))
    if short_code:
        query = query.filter(ShortUrl.short_code.ilike(f"%{short_code.strip()}%"))

    total = query.count()
    urls = (
        query.order_by(ShortUrl.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedUrls(
        page=page,
        page_size=page_size,
        total=total,
        items=[to_url_response(db, item) for item in urls],
    )


@router.delete("/urls/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_any_url(
    short_code: str,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    short_url = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
    if short_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    db.delete(short_url)
    db.commit()
    return None
