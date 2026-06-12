from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.config import get_settings
from src.api.exceptions import AppError, app_error_handler
from src.api.routers import health
from src.api.routers import cards
from src.api.routers import meetings
from src.api.routers import emails

settings = get_settings()

app = FastAPI(
    title="Relay — AI Sales Follow-up Assistant",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(health.router)
app.include_router(cards.router)
app.include_router(meetings.router)
app.include_router(emails.router)
