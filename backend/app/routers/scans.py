from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Scan, RemediationItem
from app.schemas import (
    ScanCreate,
    ScanResult,
    ScanListItem,
    ExposureHistoryPoint,
    RemediationItemCreate,
    RemediationItemUpdate,
    RemediationItemResponse,
)
from app.services.hibp import HIBPService
from app.services.data_brokers import DataBrokerService
from app.services.action_plan import ActionPlanService

router = APIRouter(prefix="/api/scans", tags=["scans"])


def _exposure_score(breach_count: int, paste_count: int, broker_flags: int) -> float:
    """Compute 0-100 exposure score from signals."""
    score = min(100.0, breach_count * 15 + paste_count * 10 + broker_flags * 3)
    return round(score, 1)


@router.post("", response_model=ScanResult)
async def create_scan(
    body: ScanCreate,
    db: AsyncSession = Depends(get_db),
):
    hibp = HIBPService()
    brokers = DataBrokerService()
    plan_svc = ActionPlanService()

    account = body.email_or_username.strip()
    if not account:
        raise HTTPException(status_code=400, detail="email_or_username required")

    breaches, breaches_ok = await hibp.get_breaches_for_account(account)
    pastes, pastes_ok = await hibp.get_pastes_for_account(account)
    
    # Use mock data if HIBP is unavailable (no API key or rate limited)
    if not breaches_ok:
        breaches = hibp._mock_breaches(account)
    if not pastes_ok:
        pastes = hibp._mock_pastes(account)
    
    broker_list = brokers.get_brokers_for_account(account)
    broker_count = len(broker_list)

    action_plan = await plan_svc.generate(
        account, breaches, pastes, broker_count
    )

    score = _exposure_score(len(breaches), len(pastes), broker_count)
    raw_results = {
        "breaches": breaches,
        "pastes": pastes,
        "data_brokers": broker_list,
        "demo_mode": not (breaches_ok and pastes_ok),
        "hibp_unavailable": not (breaches_ok and pastes_ok),
    }

    scan = Scan(
        email_or_username=account,
        exposure_score=score,
        breach_count=len(breaches),
        paste_count=len(pastes),
        data_broker_flags=broker_count,
        raw_results=raw_results,
        action_plan=action_plan,
    )
    db.add(scan)
    await db.flush()

    # Persist action plan as remediation items
    for action in action_plan.get("actions", []):
        item = RemediationItem(
            scan_id=scan.id,
            title=action.get("title", ""),
            category=action.get("category", "other"),
            priority=action.get("priority", 2),
            link_or_instruction=action.get("link_or_instruction"),
        )
        db.add(item)
    await db.flush()
    await db.refresh(scan)
    return scan


@router.get("", response_model=list[ScanListItem])
async def list_scans(
    email_or_username: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    q = select(Scan).order_by(desc(Scan.created_at)).limit(limit)
    if email_or_username:
        q = q.where(Scan.email_or_username == email_or_username.strip())
    r = await db.execute(q)
    return list(r.scalars().all())


@router.get("/history", response_model=list[ExposureHistoryPoint])
async def exposure_history(
    email_or_username: str,
    limit: int = 30,
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Scan)
        .where(Scan.email_or_username == email_or_username.strip())
        .order_by(desc(Scan.created_at))
        .limit(limit)
    )
    r = await db.execute(q)
    scans = list(r.scalars().all())
    return [
        ExposureHistoryPoint(
            date=s.created_at.strftime("%Y-%m-%d"),
            exposure_score=s.exposure_score,
            scan_id=s.id,
        )
        for s in reversed(scans)
    ]


@router.get("/{scan_id}", response_model=ScanResult)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = r.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan


@router.get("/{scan_id}/remediation", response_model=list[RemediationItemResponse])
async def list_remediation(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(
        select(RemediationItem).where(RemediationItem.scan_id == scan_id)
    )
    return list(r.scalars().all())


@router.patch("/{scan_id}/remediation/{item_id}", response_model=RemediationItemResponse)
async def update_remediation(
    scan_id: int,
    item_id: int,
    body: RemediationItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(
        select(RemediationItem).where(
            RemediationItem.id == item_id,
            RemediationItem.scan_id == scan_id,
        )
    )
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Remediation item not found")
    if body.completed is not None:
        item.completed = body.completed
        if body.completed:
            from datetime import datetime
            item.completed_at = datetime.utcnow()
    await db.flush()
    await db.refresh(item)
    return item
