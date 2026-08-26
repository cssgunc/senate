"""Analytics schemas — pageview ingest and admin summary DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PageViewCreateDTO(BaseModel):
    path: str
    referrer_host: str | None = None
    user_agent: str | None = None
    visitor_hash: str


class DailyPageViewCountDTO(BaseModel):
    day: datetime
    count: int

    model_config = ConfigDict(from_attributes=True)


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
