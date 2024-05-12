from __future__ import annotations
from typing import List
from uuid import UUID
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Table
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

association_table = Table(
    "roles2users",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("added_on", DateTime(), default=datetime.now)
)

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    guild_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("guilds.id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_on: Mapped[datetime] = mapped_column(default=datetime.now)
    
    users: Mapped[List[User]] = relationship(
        secondary=association_table, back_populates="roles", lazy="subquery", cascade="all,delete"
    )
    
    def __eq__(self, other: Role) -> bool:
        return self.id == other.id
    
    def __repr__(self) -> str:
        return f"ID: {self.id}, Name: {self.name}"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    roles: Mapped[List[Role]] = relationship(
        secondary=association_table, back_populates="users", lazy="subquery", cascade="all,delete"
    )
    
    def __eq__(self, other: User) -> bool:
        return self.id == other.id
    
    def __repr__(self) -> str:
        return f"ID: {self.id}"
    
class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    roles: Mapped[List[Role]] = relationship()
    
    def __eq__(self, other: Guild) -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return f"ID: {self.id}"