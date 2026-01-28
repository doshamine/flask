import atexit
import os
from datetime import datetime

from sqlalchemy import create_engine, Integer, String, DateTime, func, ForeignKey, insert
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, foreign
from flask_login import UserMixin

from auth import hash_password

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "netology_advertisements")

PG_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

class User(UserMixin, Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password
        }

    @property
    def id_dict(self):
        return {
            "id": self.id
        }


class Advertisement(Base):
    __tablename__ = "advertisement"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    header: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    @property
    def dict(self):
        return {
            "id": self.id,
            "header": self.header,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "user": self.user_id
        }

    @property
    def id_dict(self):
        return {
            "id": self.id
        }

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)

    stmt1 = insert(User).values(email="<EMAIL1>", password=hash_password("<PASSWORD1>"))
    stmt2 = insert(User).values(email="<EMAIL2>", password=hash_password("<PASSWORD2>"))

    with engine.connect() as conn:
        conn.execute(stmt1)
        conn.execute(stmt2)
        conn.commit()

    atexit.register(engine.dispose)