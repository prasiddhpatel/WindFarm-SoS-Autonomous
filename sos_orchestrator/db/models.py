"""ORM models — import Base from db.base to avoid circular imports."""
from __future__ import annotations
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

try:
    from db.base import Base
except ImportError:
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):  # type: ignore
        pass


class Turbine(Base):
    __tablename__ = 'turbines'
    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turbine_code    = Column(String(32), nullable=False, unique=True)
    name            = Column(String(128))
    latitude        = Column(Float)
    longitude       = Column(Float)
    blade_length_m  = Column(Float)
    hub_height_m    = Column(Float)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class BladePatch(Base):
    __tablename__ = 'blade_patches'
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turbine_id     = Column(UUID(as_uuid=True), ForeignKey('turbines.id'))
    blade_index    = Column(Integer)
    chord_pos      = Column(Float)
    span_pos       = Column(Float)
    defect_class   = Column(Integer, default=0)
    severity       = Column(Float,   default=0.0)
    rul_days       = Column(Float)
    recommendation = Column(String(64))
    updated_at     = Column(DateTime(timezone=True), server_default=func.now())


class FleetTask(Base):
    __tablename__ = 'fleet_tasks'
    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_type      = Column(String(64))
    robot_id       = Column(String(64))
    reward         = Column(Float, default=0.0)
    execution_cost = Column(Float, default=0.0)
    utility        = Column(Float, default=0.0)
    state          = Column(String(32), default='pending')
    created_at     = Column(DateTime(timezone=True), server_default=func.now())
