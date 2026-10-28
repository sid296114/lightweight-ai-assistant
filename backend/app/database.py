"""数据库连接：SQLAlchemy 2.0 + PyMySQL（同步引擎，FastAPI 自动放入线程池）。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """启动时建表（首期三表全建）。"""
    import app.models  # noqa: F401  确保模型已注册

    Base.metadata.create_all(bind=engine)
