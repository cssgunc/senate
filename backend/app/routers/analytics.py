"""Pageview ingest route — called server-side by the frontend's proxy.ts on
every page request. Not admin-authenticated (the proxy has no admin session),
so it is instead gated by a shared secret header and a per-IP rate limit.

POST /api/analytics/pageview — record one pageview
"""

from datetime import datetime, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import ANALYTICS_INGEST_SECRET
from app.database import get_db
from app.models.PageView import PageView
from app.schemas.analytics import PageViewCreateDTO

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

RATE_LIMIT_MAX_REQUESTS = 120
RATE_LIMIT_WINDOW = timedelta(minutes=1)
_ingest_requests: Dict[str, List[datetime]] = {}


def _check_rate_limit(client_ip: str) -> None:
    now = datetime.now()
    cutoff = now - RATE_LIMIT_WINDOW
    recent = [ts for ts in _ingest_requests.get(client_ip, []) if ts > cutoff]
    if len(recent) >= RATE_LIMIT_MAX_REQUESTS:
        _ingest_requests[client_ip] = recent
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests")
    recent.append(now)
    _ingest_requests[client_ip] = recent


def _verify_ingest_secret(x_analytics_secret: str | None = Header(default=None)) -> None:
    if not ANALYTICS_INGEST_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics ingest is not configured",
        )
    if x_analytics_secret != ANALYTICS_INGEST_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingest secret")


@router.post("/pageview", status_code=status.HTTP_204_NO_CONTENT)
def create_pageview(
    body: PageViewCreateDTO,
    request: Request,
    db: Session = Depends(get_db),
    _secret: None = Depends(_verify_ingest_secret),
):
    """Record one pageview. Fire-and-forget from the caller's perspective."""
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    view = PageView(
        path=body.path,
        referrer_host=body.referrer_host,
        user_agent=body.user_agent,
        visitor_hash=body.visitor_hash,
    )
    db.add(view)
    db.commit()
