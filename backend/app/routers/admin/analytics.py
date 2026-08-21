"""Admin analytics routes.

GET /api/admin/analytics/summary — aggregated pageview stats for the dashboard
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.PageView import PageView
from app.schemas.analytics import (
    AnalyticsSummaryDTO,
    DailyPageViewCountDTO,
    TopPathDTO,
    TopReferrerDTO,
)

router = APIRouter(prefix="/api/admin/analytics", tags=["admin", "analytics"])

TOP_N = 10


@router.get("/summary", response_model=AnalyticsSummaryDTO)
def get_analytics_summary(
    days: int = Query(default=7, ge=1, le=90, description="Number of trailing days to summarize"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate pageview stats over the trailing `days` days."""
    cutoff = datetime.now() - timedelta(days=days)
    in_range = PageView.created_at >= cutoff

    total_pageviews = db.query(PageView).filter(in_range).count()
    unique_visitors = (
        db.query(PageView.visitor_hash).filter(in_range).distinct().count()
    )

    day_col = func.date(PageView.created_at).label("day")
    daily_rows = (
        db.query(day_col, func.count(PageView.id).label("count"))
        .filter(in_range)
        .group_by(day_col)
        .order_by(day_col)
        .all()
    )

    top_path_rows = (
        db.query(PageView.path, func.count(PageView.id).label("count"))
        .filter(in_range)
        .group_by(PageView.path)
        .order_by(func.count(PageView.id).desc())
        .limit(TOP_N)
        .all()
    )

    top_referrer_rows = (
        db.query(PageView.referrer_host, func.count(PageView.id).label("count"))
        .filter(in_range, PageView.referrer_host.isnot(None))
        .group_by(PageView.referrer_host)
        .order_by(func.count(PageView.id).desc())
        .limit(TOP_N)
        .all()
    )

    return AnalyticsSummaryDTO(
        range_days=days,
        total_pageviews=total_pageviews,
        unique_visitors=unique_visitors,
        daily_pageviews=[DailyPageViewCountDTO(day=row.day, count=row.count) for row in daily_rows],
        top_paths=[TopPathDTO(path=row.path, count=row.count) for row in top_path_rows],
        top_referrers=[
            TopReferrerDTO(referrer_host=row.referrer_host, count=row.count)
            for row in top_referrer_rows
        ],
    )
