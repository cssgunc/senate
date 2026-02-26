"""CMS models: News, Committee, CommitteeMembership, Staff, StaticPageContent, AppConfig

These models form the CMS backbone of the Senate application (TDD Section 4.4).
Admin users manage all of these through the dashboard.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

# Admin and Senator are defined in the Core Entities models (issue #3).
# TYPE_CHECKING imports are never executed at runtime, so there is no circular
# import or ModuleNotFoundError.  from __future__ import annotations ensures
# that every annotation in this file is evaluated lazily (as a string), so
# Mapped[Admin] and Mapped[Senator] also do not raise NameError at runtime.
if TYPE_CHECKING:
    from app.models import Admin, Senator  # noqa: F401


class News(Base):
    """Published news articles displayed on the homepage and news page.

    Admin users can create, edit, and delete news articles. The is_published
    flag controls draft vs. live state. date_last_edited auto-updates on save.
    """

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # Nullable FK — author may not be present if the admin account is deleted
    author_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("admin.id", ondelete="SET NULL"), nullable=True
    )
    date_published: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    date_last_edited: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    author: Mapped[Optional[Admin]] = relationship("Admin", back_populates="news_articles")

    def __repr__(self) -> str:
        return f"<News id={self.id} title={self.title!r} published={self.is_published}>"


class Committee(Base):
    """Senate standing and special committees.

    chair_senator_id is nullable — chair_name/chair_email serve as fallback
    display fields when the chair is not represented in the Senator table.
    """

    __tablename__ = "committee"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    # Nullable FK — chair may not be a tracked Senator
    chair_senator_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("senator.id", ondelete="SET NULL"), nullable=True
    )
    chair_name: Mapped[str] = mapped_column(String(200), nullable=False)
    chair_email: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    chair_senator: Mapped[Optional[Senator]] = relationship(
        "Senator", foreign_keys=[chair_senator_id]
    )
    memberships: Mapped[list["CommitteeMembership"]] = relationship(
        "CommitteeMembership", back_populates="committee", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Committee id={self.id} name={self.name!r} active={self.is_active}>"


class CommitteeMembership(Base):
    """Many-to-many relationship between Senators and Committees.

    A senator can only belong to a given committee once — enforced by the
    composite unique constraint on (senator_id, committee_id).
    The role field captures position within the committee (e.g. Member, Vice Chair).
    """

    __tablename__ = "committee_membership"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    senator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("senator.id", ondelete="CASCADE"), nullable=False
    )
    committee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("committee.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(255), nullable=False, default="Member")

    __table_args__ = (
        UniqueConstraint("senator_id", "committee_id", name="uq_committee_membership"),
    )

    # Relationships
    senator: Mapped[Senator] = relationship("Senator", back_populates="committee_memberships")
    committee: Mapped["Committee"] = relationship("Committee", back_populates="memberships")

    def __repr__(self) -> str:
        return (
            f"<CommitteeMembership senator_id={self.senator_id} "
            f"committee_id={self.committee_id} role={self.role!r}>"
        )


class Staff(Base):
    """Non-senator staff members displayed on the About page.

    display_order controls ordering in the staff directory listing.
    is_active allows soft-removal without destroying records.
    """

    __tablename__ = "staff"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Staff id={self.id} name={self.first_name!r} {self.last_name!r} active={self.is_active}>"


class StaticPageContent(Base):
    """Editable content blocks for static/informational pages.

    page_slug is unique and serves as the URL identifier, e.g.
    "powers-of-senate", "how-a-bill-becomes-law", "public-disclosure".
    body stores HTML or Markdown content edited via the admin dashboard.
    """

    __tablename__ = "static_page_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    page_slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    last_edited_by: Mapped[int] = mapped_column(Integer, ForeignKey("admin.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    editor: Mapped[Admin] = relationship("Admin", back_populates="edited_pages")

    def __repr__(self) -> str:
        return f"<StaticPageContent id={self.id} slug={self.page_slug!r}>"


class AppConfig(Base):
    """Key-value store for site-wide configuration toggles.

    key is unique — examples: "staffer_app_open", "finance_hearing_active".
    value is always stored as a string; callers are responsible for parsing
    (e.g. "true"/"false" for booleans, ISO dates for dates).
    """

    __tablename__ = "app_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    updated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin.id", ondelete="RESTRICT"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # Relationships
    updater: Mapped[Admin] = relationship("Admin", back_populates="config_updates")

    def __repr__(self) -> str:
        return f"<AppConfig id={self.id} key={self.key!r} value={self.value!r}>"
