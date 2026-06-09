import os
from contextlib import asynccontextmanager
from urllib.parse import quote_plus

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


load_dotenv()


def build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_engine = os.getenv("DB_ENGINE", "sqlite").lower()
    if db_engine == "mysql":
        user = os.getenv("MYSQL_USER", "root")
        password = quote_plus(os.getenv("MYSQL_PASSWORD", "root"))
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DATABASE", "url_shortener")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    return "sqlite:///./url_shortener.db"


DATABASE_URL = build_database_url()

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_roles(db: Session) -> None:
    from app.models import Role

    for role_name in ("admin", "user"):
        role = db.query(Role).filter(Role.role_name == role_name).first()
        if role is None:
            db.add(Role(role_name=role_name))
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import models

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()
    yield
