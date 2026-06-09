from fastapi import FastAPI

from app.database import lifespan
from app.routers import admin, analytics, auth, urls


def create_app() -> FastAPI:
    app = FastAPI(
        title="URL Shortener Service",
        version="1.0.0",
        description="FastAPI team task with JWT auth, URL management, analytics, search, pagination, and roles.",
        lifespan=lifespan,
    )

    app.include_router(auth.router)
    app.include_router(auth.profile_router)
    app.include_router(urls.router)
    app.include_router(admin.router)
    app.include_router(analytics.router)
    app.include_router(urls.redirect_router)

    return app


app = create_app()
