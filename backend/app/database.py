"""Database configuration and session management"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MSSQL_SA_PASSWORD", "SenateDev2026!")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "senate")
SQLALCHEMY_ECHO = _env_bool("SQLALCHEMY_ECHO", default=False)

DATABASE_URL = os.getenv("DATABASE_URL")
ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("MODE", "development")).lower()
if ENVIRONMENT == "production" and not DATABASE_URL and not (
    os.getenv("DB_PASSWORD") or os.getenv("MSSQL_SA_PASSWORD")
):
    raise RuntimeError(
        "DB_PASSWORD or MSSQL_SA_PASSWORD is required when ENVIRONMENT=production"
    )

if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql+psycopg2://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

engine = create_engine(DATABASE_URL, echo=SQLALCHEMY_ECHO, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
