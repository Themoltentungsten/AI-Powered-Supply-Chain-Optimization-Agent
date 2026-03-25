# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Async PostgreSQL engine (initial scaffold)
#  DAY 2: Switched to sync SQLAlchemy + SQLite for local dev
# ═══════════════════════════════════════════════════════════════════════

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from .config import get_settings

settings = get_settings()

# ── DAY 2 START: Sync engine with SQLite / PostgreSQL support ────────
_connect_args = {}
if "sqlite" in settings.database_url:
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args=_connect_args,
)

if "sqlite" in str(engine.url):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
# ── DAY 2 END ────────────────────────────────────────────────────────


# ── DAY 1 START: Base class and helpers ──────────────────────────────
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
# ── DAY 1 END ────────────────────────────────────────────────────────
