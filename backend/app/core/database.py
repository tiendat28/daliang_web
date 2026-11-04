from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ten index KHONG kem schema (ix_<bang>_<cot>): bang chuyen tu public sang
# schema cua module (Alembic 0001) giu nguyen ten index cu, va ten bang da la
# duy nhat tren ca he thong.
Base = declarative_base(metadata=MetaData(naming_convention={"ix": "ix_%(table_name)s_%(column_0_name)s"}))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
