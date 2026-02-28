from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ScanCreate(BaseModel):
    email_or_username: str


class BreachSummary(BaseModel):
    name: str
    date: Optional[str] = None
    data_classes: Optional[list[str]] = None


class ScanResult(BaseModel):
    id: int
    email_or_username: str
    exposure_score: float
    breach_count: int
    paste_count: int
    data_broker_flags: int
    raw_results: Optional[dict] = None
    action_plan: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScanListItem(BaseModel):
    id: int
    email_or_username: str
    exposure_score: float
    breach_count: int
    paste_count: int
    data_broker_flags: int
    created_at: datetime

    class Config:
        from_attributes = True


class RemediationItemCreate(BaseModel):
    title: str
    category: str
    priority: int = 1
    link_or_instruction: Optional[str] = None


class RemediationItemUpdate(BaseModel):
    completed: Optional[bool] = None


class RemediationItemResponse(BaseModel):
    id: int
    scan_id: int
    title: str
    category: str
    priority: int
    link_or_instruction: Optional[str] = None
    completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExposureHistoryPoint(BaseModel):
    date: str
    exposure_score: float
    scan_id: int
