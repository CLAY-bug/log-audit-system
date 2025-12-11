from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

    # CORS：第 1 周先全开放，后续按域名收紧。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    def health_check():
        return {"status": "ok"}

    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = create_application()
