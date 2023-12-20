from typing import AsyncGenerator

from sqlalchemy import (
    TIMESTAMP, MetaData, String, Integer, ForeignKey, Boolean
)
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
)
from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import (
    DeclarativeBase, mapped_column, Mapped, relationship
)
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./database.db"


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

metadata = MetaData()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Generates a new asynchronous session."""
    async with async_session_maker() as session:
        yield session


# Models
class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headling: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    pub_date: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.utcnow
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(
            "recipes_user.id", 
            ondelete="CASCADE"
        ), nullable=False, unique=False
    )
    author: Mapped["User"] = relationship(
        back_populates="recipes", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("length(text) >= 10",
                        name="text_min_length"),
        CheckConstraint("length(headling) >= 10",
                        name="headling_min_length"),
    )


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "recipes_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String, nullable=False, unique=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="author", lazy="selectin"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    def __repr__(self) -> str:
        return self.username
