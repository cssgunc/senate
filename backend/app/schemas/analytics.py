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
