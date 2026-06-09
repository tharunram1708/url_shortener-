from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ShortUrl, UrlLog, User
from app.schemas import PaginatedUrls, UrlCreateRequest, UrlResponse, UrlUpdateRequest
from app.security import get_current_user
from app.url_helpers import clean_short_code, get_owned_url_or_404, make_short_code, to_url_response


router = APIRouter(prefix="/urls", tags=["URLs"])
redirect_router = APIRouter(tags=["Redirects"])


@router.post("", response_model=UrlResponse, status_code=status.HTTP_201_CREATED)
def create_short_url(
    payload: UrlCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    short_code = clean_short_code(payload.custom_code) if payload.custom_code else make_short_code(db)
    code_exists = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
    if code_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Short code already exists")

    short_url = ShortUrl(
        original_url=str(payload.original_url),
        short_code=short_code,
        created_by=current_user.id,
    )
    db.add(short_url)
    db.commit()
    db.refresh(short_url)
    return to_url_response(db, short_url)


@router.get("", response_model=PaginatedUrls)
def list_urls(
    original_url: str | None = Query(default=None, description="Search inside the original URL"),
    short_code: str | None = Query(default=None, description="Search inside the short code"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    view_all: bool = Query(default=False, description="Admins can set this to true"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ShortUrl)
    if current_user.role.role_name != "admin" or not view_all:
        query = query.filter(ShortUrl.created_by == current_user.id)

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


@router.get("/{short_code}", response_model=UrlResponse)
def get_url_details(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    short_url = get_owned_url_or_404(db, short_code, current_user)
    return to_url_response(db, short_url)


@router.put("/{short_code}", response_model=UrlResponse)
def update_short_url(
    short_code: str,
    payload: UrlUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    short_url = get_owned_url_or_404(db, short_code, current_user)

    if payload.original_url is not None:
        short_url.original_url = str(payload.original_url)

    if payload.short_code is not None:
        new_code = clean_short_code(payload.short_code)
        code_exists = db.query(ShortUrl).filter(ShortUrl.short_code == new_code).first()
        if code_exists and code_exists.id != short_url.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Short code already exists")
        short_url.short_code = new_code

    db.commit()
    db.refresh(short_url)
    return to_url_response(db, short_url)


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_short_url(
    short_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    short_url = get_owned_url_or_404(db, short_code, current_user)
    db.delete(short_url)
    db.commit()
    return None


@redirect_router.get("/{short_code}", include_in_schema=False)
def open_short_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    short_url = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
    if short_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    ip_address = request.client.host if request.client else None
    short_url.click_count += 1
    db.add(UrlLog(url_id=short_url.id, ip_address=ip_address))
    db.commit()

    return RedirectResponse(short_url.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
