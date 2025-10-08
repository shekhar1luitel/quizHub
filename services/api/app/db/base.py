from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


# Import models so Alembic can discover metadata during autogenerate
from app import models  # noqa: F401,E402
