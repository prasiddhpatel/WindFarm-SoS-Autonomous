from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import String, Float, DateTime, Text, ForeignKey, SmallInteger
from sqlalchemy.sql import func
import uuid


class Base(DeclarativeBase):
    pass


class Turbine(Base):
    __tablename__ = "turbines"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turbine_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    blade_length_m: Mapped[float] = mapped_column(Float, nullable=False)
    hub_height_m: Mapped[float] = mapped_column(Float, nullable=False)


class BladePatch(Base):
    __tablename__ = "blade_patches"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turbine_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("turbines.id", ondelete="CASCADE"), nullable=False)
    blade_index: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    chord_pos: Mapped[float] = mapped_column(Float, nullable=False)
    span_pos: Mapped[float] = mapped_column(Float, nullable=False)
    defect_class: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
    severity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    severity_cov: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rul_cycles: Mapped[float | None] = mapped_column(Float)
    rul_days: Mapped[float | None] = mapped_column(Float)
    recommendation: Mapped[str | None] = mapped_column(String)


class FleetTask(Base):
    __tablename__ = "fleet_tasks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    robot_id: Mapped[str | None] = mapped_column(String)
    reward: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    execution_cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    utility: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    state: Mapped[str] = mapped_column(String, nullable=False, default="queued")
    constraints: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
