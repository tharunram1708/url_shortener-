from datetime import datetime
import secrets
import string

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import ShortUrl, User, UrlLog
from app.schemas import UrlResponse, UserResponse


def clean_short_code(short_code: str) -> str:
    allowed = set(string.ascii_letters + string.digits + "-_")
    if not short_code or any(character not in allowed for character in short_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Short code can only contain letters, numbers, hyphen, and underscore",
        )
    return short_code


def make_short_code(db: Session, length: int = 7) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        short_code = "".join(secrets.choice(alphabet) for _ in range(length))
        exists = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
        if not exists:
            return short_code


def get_last_accessed_at(db: Session, url_id: int) -> datetime | None:
    return db.query(func.max(UrlLog.accessed_at)).filter(UrlLog.url_id == url_id).scalar()


def to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role_name=user.role.role_name,
    )


def to_url_response(db: Session, short_url: ShortUrl) -> UrlResponse:
    return UrlResponse(
        id=short_url.id,
        original_url=short_url.original_url,
        short_code=short_url.short_code,
        click_count=short_url.click_count,
        created_by=short_url.created_by,
        created_at=short_url.created_at,
        last_accessed_at=get_last_accessed_at(db, short_url.id),
    )


def get_owned_url_or_404(db: Session, short_code: str, current_user: User) -> ShortUrl:
    short_url = db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
    if short_url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    is_admin = current_user.role.role_name == "admin"
    if not is_admin and short_url.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can manage only your own URLs")

    return short_url
