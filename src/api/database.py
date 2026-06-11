from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.api.config import get_settings


@lru_cache
def _get_engine():
    return create_engine(get_settings().database_url)


@lru_cache
def _get_session_factory():
    return sessionmaker(autocommit=False, autoflush=False, bind=_get_engine())


def get_db() -> Generator[Session, None, None]:
    db = _get_session_factory()()
    try:
        yield db
    finally:
        db.close()
