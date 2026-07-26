"""SQLAlchemy ORM models.

Only raw observations are stored. Derived fields (change vs 1/2/5 years ago,
trend colour) are computed at read time in `derive.py` rather than persisted,
so the raw series stays the single source of truth.
"""

from __future__ import annotations

from datetime import date as date_

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(32))
    unit: Mapped[str] = mapped_column(String(16))
    direction: Mapped[str] = mapped_column(String(16))
    note: Mapped[str] = mapped_column(String(256))

    observations: Mapped[list[Observation]] = relationship(
        back_populates="indicator",
        cascade="all, delete-orphan",
        order_by="Observation.date",
    )


class Observation(Base):
    __tablename__ = "observations"
    __table_args__ = (
        UniqueConstraint("indicator_id", "date", name="uq_observation_indicator_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id"))
    date: Mapped[date_]
    value: Mapped[float]

    indicator: Mapped[Indicator] = relationship(back_populates="observations")
