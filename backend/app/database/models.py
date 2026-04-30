"""
AquaIntelli - SQL Database Models (SQLAlchemy ORM)
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped
from .sql_db import Base


class GroundwaterReading(Base):
    __tablename__ = "groundwater_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    district: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    depth_m: Mapped[float] = mapped_column(Float)
    grace_anomaly_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_moisture_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rainfall_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BorewellPrediction(Base):
    __tablename__ = "borewell_predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    district: Mapped[str] = mapped_column(String(100), default="unknown")
    soil_type: Mapped[str] = mapped_column(String(50))
    requested_depth_m: Mapped[float] = mapped_column(Float)
    success_probability: Mapped[float] = mapped_column(Float)
    recommended_depth_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WaterCrisisAlert(Base):
    __tablename__ = "water_crisis_alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    district: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    source_satellite: Mapped[str] = mapped_column(String(50), default="GRACE-FO")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IrrigationRecommendation(Base):
    __tablename__ = "irrigation_recommendations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    crop_type: Mapped[str] = mapped_column(String(50))
    etc_mm_per_day: Mapped[float] = mapped_column(Float)
    kc: Mapped[float] = mapped_column(Float)
    eto_mm_per_day: Mapped[float] = mapped_column(Float)
    irrigation_required_mm: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExchangeOrder(Base):
    __tablename__ = "exchange_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    asset_id: Mapped[str] = mapped_column(String(20))
    side: Mapped[str] = mapped_column(String(10))  # BUY / SELL
    quantity_ml: Mapped[float] = mapped_column(Float)
    price_per_ml: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    user_id: Mapped[str] = mapped_column(String(100), default="DEMO_USER")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FarmField(Base):
    __tablename__ = "farm_fields"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    crop_type: Mapped[str] = mapped_column(String(50))
    area_hectares: Mapped[float] = mapped_column(Float, default=1.0)
    soil_moisture_pct: Mapped[float] = mapped_column(Float, default=45.0)
    irrigation_status: Mapped[str] = mapped_column(String(30), default="SCHEDULED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
