from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_or_username: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    exposure_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    breach_count: Mapped[int] = mapped_column(Integer, default=0)
    paste_count: Mapped[int] = mapped_column(Integer, default=0)
    data_broker_flags: Mapped[int] = mapped_column(Integer, default=0)
    raw_results: Mapped[dict] = mapped_column(JSON, nullable=True)  # breaches, pastes, broker hints
    action_plan: Mapped[dict] = mapped_column(JSON, nullable=True)  # AI-generated actions
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    remediation_progress: Mapped[list["RemediationItem"]] = relationship(
        "RemediationItem", back_populates="scan", cascade="all, delete-orphan"
    )


class RemediationItem(Base):
    __tablename__ = "remediation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scan_id: Mapped[int] = mapped_column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)  # opt_out, password_change, delete_account, etc.
    priority: Mapped[int] = mapped_column(Integer, default=1)  # 1=high, 2=medium, 3=low
    link_or_instruction: Mapped[str] = mapped_column(Text, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scan: Mapped["Scan"] = relationship("Scan", back_populates="remediation_progress")
