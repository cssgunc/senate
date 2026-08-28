"""Analytics schemas — pageview ingest and admin summary DTOs."""

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator


class PageViewCreateDTO(BaseModel):
    path: str
    referrer_host: str | None = None
    user_agent: str | None = None
    visitor_hash: str


class DailyPageViewCountDTO(BaseModel):
    day: datetime
    count: int

    model_config = ConfigDict(from_attributes=True)

    # created_at is stored naive in the DB (UTC). Attach UTC tzinfo so the
    # serialized timestamp carries an offset and clients parse it correctly
    # instead of misreading it as local time.
    @field_validator("day")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


class ActiveUsersDTO(BaseModel):
    active_users: int


class TopPathDTO(BaseModel):
    path: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class TopReferrerDTO(BaseModel):
    referrer_host: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class AnalyticsSummaryDTO(BaseModel):
    range_days: int
    total_pageviews: int
    unique_visitors: int
    daily_pageviews: list[DailyPageViewCountDTO]
    top_paths: list[TopPathDTO]
    top_referrers: list[TopReferrerDTO]


class NavigationFlowLinkDTO(BaseModel):
    source: str
    target: str
    count: int

    model_config = ConfigDict(from_attributes=True)


class NavigationFlowDTO(BaseModel):
    range_days: int
    total_sessions: int
    links: list[NavigationFlowLinkDTO]


class UptimeCheckCreateDTO(BaseModel):
    target: str
    is_up: bool
    latency_ms: float | None = None
    error: str | None = None


class UptimeBucketDTO(BaseModel):
    bucket: datetime
    total_checks: int
    up_checks: int
    uptime_pct: float

    model_config = ConfigDict(from_attributes=True)

    @field_validator("bucket")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


class UptimeIncidentDTO(BaseModel):
    target: str
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: float | None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("started_at", "ended_at")
    @classmethod
    def _ensure_utc(cls, value: datetime | None) -> datetime | None:
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=timezone.utc)


class TargetUptimeDTO(BaseModel):
    target: str
    uptime_pct: float
    buckets: list[UptimeBucketDTO]


class UptimeSummaryDTO(BaseModel):
    range_days: int
    overall_uptime_pct: float
    targets: list[TargetUptimeDTO]
    incidents: list[UptimeIncidentDTO]
