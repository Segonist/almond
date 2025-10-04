from sqlalchemy import BigInteger, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class Mode(Base):
    __tablename__ = "mode"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    victories: Mapped[list["Victory"]] = relationship("Victory", back_populates="mode")
    updatable_messages: Mapped[list["UpdatableMessage"]] = relationship(
        "UpdatableMessage", back_populates="mode"
    )

    def __repr__(self) -> str:
        return f"Mode(id={self.id}, name={self.name!r}, guild_id={self.guild_id})"


class Victory(Base):
    __tablename__ = "victory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mode_id: Mapped[int] = mapped_column(Integer, ForeignKey("mode.id"), nullable=False)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    mode: Mapped["Mode"] = relationship("Mode", back_populates="victories")

    def __repr__(self) -> str:
        return f"Victory(id={self.id}, user_id={self.user_id}, mode_id={self.mode_id}, guild_id={self.guild_id})"


class UpdatableMessage(Base):
    __tablename__ = "updatable_message"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mode_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("mode.id"), nullable=True
    )
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    mode: Mapped["Mode"] = relationship("Mode", back_populates="updatable_messages")

    def __repr__(self) -> str:
        return f"UpdatableMessage(id={self.id}, channel_id={self.channel_id}, message_id={self.message_id}, mode_id={self.mode_id} guild_id={self.guild_id})"
