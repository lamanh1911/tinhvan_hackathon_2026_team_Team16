from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.config import get_settings


def _normalize_db_url(url: str) -> str:
    # Railway/Heroku may expose the legacy 'postgres://' scheme; SQLAlchemy
    # requires 'postgresql://'. Normalize so the managed DATABASE_URL works as-is.
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


@lru_cache
def _get_engine():
    return create_engine(_normalize_db_url(get_settings().database_url))


@lru_cache
def _get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())


def get_db() -> Generator[Session, None, None]:
    db = _get_session_factory()()
    try:
        yield db
    finally:
        db.close()
