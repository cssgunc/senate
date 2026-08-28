"""Admin analytics routes.

GET /api/admin/analytics/summary — aggregated pageview stats for the dashboard
GET /api/admin/analytics/active — count of visitors active in the trailing window
GET /api/admin/analytics/navigation-flow — page-to-page transition counts for the flow diagram
GET /api/admin/analytics/uptime — uptime percentage and incidents from the uptime-probe CronJob
"""

import itertools
from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.PageView import PageView
from app.models.UptimeCheck import UptimeCheck
from app.schemas.analytics import (
    ActiveUsersDTO,
    AnalyticsSummaryDTO,
    DailyPageViewCountDTO,
    NavigationFlowDTO,
    NavigationFlowLinkDTO,
    TargetUptimeDTO,
    TopPathDTO,
    TopReferrerDTO,
    UptimeBucketDTO,
    UptimeIncidentDTO,
    UptimeSummaryDTO,
)

router = APIRouter(prefix="/api/admin/analytics", tags=["admin", "analytics"])

TOP_N = 10
ACTIVE_WINDOW_MINUTES = 5
UPTIME_TARGETS = ["backend", "frontend"]
MAX_INCIDENTS = 20

# Start-edges and page-edges share one ranked pool, so this needs to be higher
# than TOP_N to leave room for both to render a legible flow diagram.
NAV_FLOW_TOP_N = 20
SESSION_GAP_MINUTES = 30
SESSION_START_SENTINEL = "__start__"


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

    # A 1-day range is bucketed by hour (daily buckets would collapse to one point).
    # Buckets are computed in the database's session timezone (UTC in production);
    # DailyPageViewCountDTO attaches UTC tzinfo so clients render them in local time.
    bucket_col = (
        func.date_trunc("hour", PageView.created_at).label("day")
        if days <= 1
        else func.date(PageView.created_at).label("day")
    )
    daily_rows = (
        db.query(bucket_col, func.count(PageView.id).label("count"))
        .filter(in_range)
        .group_by(bucket_col)
        .order_by(bucket_col)
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


@router.get("/active", response_model=ActiveUsersDTO)
def get_active_users(
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Count distinct visitors seen in the trailing ACTIVE_WINDOW_MINUTES minutes."""
    cutoff = datetime.now() - timedelta(minutes=ACTIVE_WINDOW_MINUTES)
    active_users = (
        db.query(PageView.visitor_hash)
        .filter(PageView.created_at >= cutoff)
        .distinct()
        .count()
    )
    return ActiveUsersDTO(active_users=active_users)


def _break_cycles(
    ranked_edges: list[tuple[tuple[str, str], int]],
) -> list[tuple[tuple[str, str], int]]:
    """Greedily keep the heaviest edges that don't close a cycle.

    Sankey layout requires a DAG: recharts computes each node's column via
    recursion over its outgoing edges, which stack-overflows on a cycle (e.g.
    "/" -> "/about" -> "/", common in real navigation data where visitors go
    back and forth). `ranked_edges` must already be sorted by descending
    weight; an edge is dropped if its target can already reach its source in
    the subgraph accepted so far, since adding it would close a cycle.
    """
    adjacency: dict[str, set[str]] = {}
    accepted: list[tuple[tuple[str, str], int]] = []

    def reaches(start: str, goal: str) -> bool:
        stack = [start]
        seen = {start}
        while stack:
            node = stack.pop()
            if node == goal:
                return True
            for neighbor in adjacency.get(node, ()):
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        return False

    for (src, dst), count in ranked_edges:
        if reaches(dst, src):
            continue
        adjacency.setdefault(src, set()).add(dst)
        accepted.append(((src, dst), count))

    return accepted


@router.get("/navigation-flow", response_model=NavigationFlowDTO)
def get_navigation_flow(
    days: int = Query(default=7, ge=1, le=90, description="Number of trailing days to summarize"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reconstruct sessions from ordered pageviews and tally page-to-page transitions.

    PageView has no session id, so sessions are reconstructed per visitor_hash:
    a gap over SESSION_GAP_MINUTES between one visitor's consecutive pageviews
    starts a new session (contributing a SESSION_START_SENTINEL edge); shorter
    gaps contribute a page-to-page edge unless both views share the same path.
    """
    cutoff = datetime.now() - timedelta(days=days)
    rows = (
        db.query(PageView.visitor_hash, PageView.path, PageView.created_at)
        .filter(PageView.created_at >= cutoff)
        .order_by(PageView.visitor_hash, PageView.created_at, PageView.id)
        .all()
    )

    session_gap = timedelta(minutes=SESSION_GAP_MINUTES)
    transitions: Counter[tuple[str, str]] = Counter()

    for _visitor_hash, group in itertools.groupby(rows, key=lambda r: r.visitor_hash):
        previous = None
        for row in group:
            if previous is None or (row.created_at - previous.created_at) > session_gap:
                transitions[(SESSION_START_SENTINEL, row.path)] += 1
            elif previous.path != row.path:
                transitions[(previous.path, row.path)] += 1
            previous = row

    total_sessions = sum(
        count for (src, _dst), count in transitions.items() if src == SESSION_START_SENTINEL
    )

    acyclic_edges = _break_cycles(transitions.most_common(NAV_FLOW_TOP_N))

    return NavigationFlowDTO(
        range_days=days,
        total_sessions=total_sessions,
        links=[
            NavigationFlowLinkDTO(source=src, target=dst, count=count)
            for (src, dst), count in acyclic_edges
        ],
    )


def _reconstruct_incidents(db: Session, cutoff: datetime) -> list[UptimeIncidentDTO]:
    """Turn contiguous is_up=False streaks per target into incident windows.

    Walks each target's checks in order, opening an incident on the first
    down check and closing it on the next up check. A streak still open at
    the most recent check is returned with ended_at=None (ongoing) rather
    than dropped, since a target being down as of "now" is exactly what an
    admin needs to see first.
    """
    rows = (
        db.query(UptimeCheck.target, UptimeCheck.is_up, UptimeCheck.checked_at)
        .filter(UptimeCheck.checked_at >= cutoff)
        .order_by(UptimeCheck.target, UptimeCheck.checked_at)
        .all()
    )

    incidents: list[UptimeIncidentDTO] = []
    open_started_at: dict[str, datetime] = {}

    for row in rows:
        if not row.is_up:
            open_started_at.setdefault(row.target, row.checked_at)
        elif row.target in open_started_at:
            started_at = open_started_at.pop(row.target)
            incidents.append(
                UptimeIncidentDTO(
                    target=row.target,
                    started_at=started_at,
                    ended_at=row.checked_at,
                    duration_seconds=(row.checked_at - started_at).total_seconds(),
                )
            )

    for target, started_at in open_started_at.items():
        incidents.append(
            UptimeIncidentDTO(target=target, started_at=started_at, ended_at=None, duration_seconds=None)
        )

    incidents.sort(key=lambda inc: inc.started_at, reverse=True)
    return incidents[:MAX_INCIDENTS]


@router.get("/uptime", response_model=UptimeSummaryDTO)
def get_uptime_summary(
    days: int = Query(default=7, ge=1, le=90, description="Number of trailing days to summarize"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Uptime percentage, per-target history, and recent incidents.

    A total backend outage can't record itself here (the probe reports
    through the backend's own ingest endpoint), so a full outage shows up
    indirectly as a gap in checked_at wider than the probe's schedule
    rather than as explicit down rows - see deploy/cloudapps/README.md.
    """
    cutoff = datetime.now() - timedelta(days=days)
    in_range = UptimeCheck.checked_at >= cutoff

    total_checks = db.query(UptimeCheck).filter(in_range).count()
    up_checks = db.query(UptimeCheck).filter(in_range, UptimeCheck.is_up.is_(True)).count()
    overall_uptime_pct = (up_checks / total_checks * 100) if total_checks else 100.0

    # A 1-day range is bucketed by hour, same convention as /summary.
    bucket_col = (
        func.date_trunc("hour", UptimeCheck.checked_at).label("bucket")
        if days <= 1
        else func.date(UptimeCheck.checked_at).label("bucket")
    )
    up_count_expr = func.sum(case((UptimeCheck.is_up.is_(True), 1), else_=0))

    targets: list[TargetUptimeDTO] = []
    for target in UPTIME_TARGETS:
        target_filter = in_range & (UptimeCheck.target == target)

        target_total = db.query(UptimeCheck).filter(target_filter).count()
        target_up = db.query(UptimeCheck).filter(target_filter, UptimeCheck.is_up.is_(True)).count()
        target_uptime_pct = (target_up / target_total * 100) if target_total else 100.0

        bucket_rows = (
            db.query(bucket_col, func.count(UptimeCheck.id).label("total_checks"), up_count_expr.label("up_checks"))
            .filter(target_filter)
            .group_by(bucket_col)
            .order_by(bucket_col)
            .all()
        )
        buckets = [
            UptimeBucketDTO(
                bucket=row.bucket,
                total_checks=row.total_checks,
                up_checks=row.up_checks,
                uptime_pct=(row.up_checks / row.total_checks * 100) if row.total_checks else 100.0,
            )
            for row in bucket_rows
        ]
        targets.append(TargetUptimeDTO(target=target, uptime_pct=target_uptime_pct, buckets=buckets))

    return UptimeSummaryDTO(
        range_days=days,
        overall_uptime_pct=overall_uptime_pct,
        targets=targets,
        incidents=_reconstruct_incidents(db, cutoff),
    )
