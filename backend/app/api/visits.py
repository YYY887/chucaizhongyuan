from datetime import date
from ipaddress import ip_address, ip_network
from urllib.error import URLError
from urllib.request import urlopen
import json
from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.response import success_response
from app.db.database import get_db
from app.models.visit import VisitStat
from app.schemas.admin import VisitTrackRequest

router = APIRouter(prefix="/visits", tags=["visits"])
PRIVATE_NETWORKS = (
    ip_network("127.0.0.0/8"),
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("::1/128"),
    ip_network("fc00::/7"),
)


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    candidates = [item.strip() for item in forwarded_for.split(",") if item.strip()]
    if candidates:
        return candidates[0][:64]
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip[:64]
    return (request.client.host if request.client else "unknown")[:64]


def is_private_ip(value: str) -> bool:
    try:
        parsed = ip_address(value)
    except ValueError:
        return False
    return any(parsed in network for network in PRIVATE_NETWORKS)


def resolve_ip_location(value: str) -> str:
    if value in {"unknown", ""}:
        return "未知"
    if is_private_ip(value):
        return "本地/局域网"
    try:
        with urlopen(f"https://ipwho.is/{value}", timeout=2.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError):
        return "未知"

    if not payload.get("success"):
        return "未知"

    parts = [
        str(payload.get("country") or "").strip(),
        str(payload.get("region") or "").strip(),
        str(payload.get("city") or "").strip(),
    ]
    location = " / ".join([part for part in parts if part])
    return location or "未知"


@router.post("/track", response_model=dict)
def track_visit(payload: VisitTrackRequest, request: Request, db: Session = Depends(get_db)):
    path = payload.path[:255] or "/"
    today = date.today()
    client_ip = get_client_ip(request)
    location = resolve_ip_location(client_ip)
    stat = (
        db.query(VisitStat)
        .filter(
            VisitStat.visit_date == today,
            VisitStat.path == path,
            VisitStat.ip_address == client_ip,
        )
        .first()
    )
    if not stat:
        stat = VisitStat(visit_date=today, path=path, ip_address=client_ip, location=location, count=0)
        db.add(stat)
    else:
        stat.location = location
    stat.count += 1
    db.commit()
    return success_response({"tracked": True})


@router.get("/summary", response_model=dict)
def get_visit_summary(db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(VisitStat.count), 0)).scalar()
    today_total = (
        db.query(func.coalesce(func.sum(VisitStat.count), 0))
        .filter(VisitStat.visit_date == date.today())
        .scalar()
    )
    return success_response({
        "total": int(total or 0),
        "today": int(today_total or 0),
    })
