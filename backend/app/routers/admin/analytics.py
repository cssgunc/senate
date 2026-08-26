"""Admin analytics routes.

GET /api/admin/analytics/summary — aggregated pageview stats for the dashboard
GET /api/admin/analytics/active — count of visitors active in the trailing window
GET /api/admin/analytics/navigation-flow — page-to-page transition counts for the flow diagram
"""

import itertools
from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.PageView import PageView
from app.schemas.analytics import (
    ActiveUsersDTO,
    AnalyticsSummaryDTO,
    DailyPageViewCountDTO,
    NavigationFlowDTO,
    NavigationFlowLinkDTO,
    TopPathDTO,
    TopReferrerDTO,
)

router = APIRouter(prefix="/api/admin/analytics", tags=["admin", "analytics"])

TOP_N = 10
ACTIVE_WINDOW_MINUTES = 5

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
