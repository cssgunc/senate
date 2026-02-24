"""Unit tests for CMS SQLAlchemy models (TDD Section 4.4).

Coverage:
  - Table creation for all six CMS models
  - Column presence and basic constraints (nullable, unique)
  - Foreign key relationships (News→Admin, Committee→Senator, etc.)
  - CommitteeMembership many-to-many via Senator and Committee
  - Composite unique constraint on CommitteeMembership(senator_id, committee_id)
  - Unique constraint on StaticPageContent.page_slug
  - Unique constraint on AppConfig.key
  - Auto-updating date_last_edited on News modification
  - Auto-updating updated_at on StaticPageContent and AppConfig modification
"""

from datetime import datetime

import pytest
from sqlalchemy import inspect as sa_inspect, text, update
from sqlalchemy.exc import IntegrityError

from app.models.cms import AppConfig, Committee, CommitteeMembership, News, Staff, StaticPageContent


# ===========================================================================
# Table creation
# ===========================================================================


class TestTableCreation:
    """All six CMS tables must be created in the database."""

    def test_all_cms_tables_exist(self, engine):
        inspector = sa_inspect(engine)
        tables = inspector.get_table_names()
        assert "news" in tables
        assert "committee" in tables
        assert "committee_membership" in tables
        assert "staff" in tables
        assert "static_page_content" in tables
        assert "app_config" in tables

    def test_news_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("news")}
        assert cols >= {
            "id", "title", "body", "summary", "image_url",
            "author_id", "date_published", "date_last_edited", "is_published",
        }

    def test_committee_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("committee")}
        assert cols >= {
            "id", "name", "description", "chair_senator_id",
            "chair_name", "chair_email", "is_active",
        }

    def test_committee_membership_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("committee_membership")}
        assert cols >= {"id", "senator_id", "committee_id", "role"}

    def test_staff_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("staff")}
        assert cols >= {
            "id", "first_name", "last_name", "title",
            "email", "photo_url", "display_order", "is_active",
        }

    def test_static_page_content_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("static_page_content")}
        assert cols >= {"id", "page_slug", "title", "body", "last_edited_by", "updated_at"}

    def test_app_config_columns_exist(self, engine):
        inspector = sa_inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("app_config")}
        assert cols >= {"id", "key", "value", "updated_by", "updated_at"}


# ===========================================================================
# News model
# ===========================================================================


class TestNewsModel:
    """Tests for the News model."""

    def test_create_news_with_required_fields(self, session, admin):
        article = News(
            title="Senate Passes Resolution",
            body="The senate voted 25-3 in favor...",
            summary="A brief summary.",
            author_id=admin.id,
            is_published=True,
        )
        session.add(article)
        session.flush()
        assert article.id is not None

    def test_news_image_url_is_nullable(self, session, admin):
        """image_url must be optional — defaults to None."""
        article = News(
            title="No Image Article",
            body="Body text.",
            summary="Summary.",
            author_id=admin.id,
            is_published=False,
        )
        session.add(article)
        session.flush()
        assert article.image_url is None

    def test_news_author_id_is_nullable(self, session):
        """author_id may be NULL (anonymous / deleted admin)."""
        article = News(
            title="Anonymous Article",
            body="Body text.",
            summary="Summary.",
            author_id=None,
            is_published=False,
        )
        session.add(article)
        session.flush()
        assert article.id is not None
        assert article.author_id is None

    def test_news_author_relationship(self, session, admin):
        """News.author resolves to the related Admin instance."""
        article = News(
            title="Author Test",
            body="Body.",
            summary="Summary.",
            author_id=admin.id,
            is_published=True,
        )
        session.add(article)
        session.flush()
        session.refresh(article)
        assert article.author is not None
        assert article.author.id == admin.id

    def test_news_date_published_defaults_to_now(self, session):
        article = News(title="T", body="B", summary="S", is_published=False)
        session.add(article)
        session.flush()
        session.refresh(article)
        assert article.date_published is not None

    def test_news_date_last_edited_auto_updates(self, session, admin):
        """date_last_edited must change when the row is updated via the ORM."""
        article = News(
            title="Original Title",
            body="Original body.",
            summary="Summary.",
            author_id=admin.id,
            is_published=False,
        )
        session.add(article)
        session.flush()

        # Force date_last_edited to a known past date so the comparison is clear
        old_date = datetime(2020, 1, 1, 0, 0, 0)
        session.execute(
            update(News).where(News.id == article.id).values(date_last_edited=old_date)
        )
        session.refresh(article)
        assert article.date_last_edited == old_date

        # Trigger onupdate via ORM mutation
        article.title = "Updated Title"
        session.flush()
        session.refresh(article)

        assert article.date_last_edited > old_date

    def test_news_is_published_default_is_false(self, session):
        article = News(title="T", body="B", summary="S")
        session.add(article)
        session.flush()
        assert article.is_published is False

    def test_news_repr(self, session):
        article = News(title="Test", body="B", summary="S", is_published=True)
        assert "Test" in repr(article)
        assert "True" in repr(article)


# ===========================================================================
# Committee model
# ===========================================================================


class TestCommitteeModel:
    """Tests for the Committee model."""

    def test_create_committee(self, session):
        c = Committee(
            name="Rules Committee",
            description="Governs senate procedures.",
            chair_name="Speaker Smith",
            chair_email="smith@unc.edu",
            is_active=True,
        )
        session.add(c)
        session.flush()
        assert c.id is not None

    def test_committee_chair_senator_id_is_nullable(self, session):
        """chair_senator_id may be NULL if chair is not a tracked senator."""
        c = Committee(
            name="Ad Hoc Committee",
            description="Temporary committee.",
            chair_senator_id=None,
            chair_name="External Chair",
            chair_email="external@unc.edu",
        )
        session.add(c)
        session.flush()
        assert c.chair_senator_id is None

    def test_committee_chair_senator_relationship(self, session, senator):
        """Committee.chair_senator resolves to the related Senator instance."""
        c = Committee(
            name="Finance",
            description="Finance matters.",
            chair_senator_id=senator.id,
            chair_name=f"{senator.first_name} {senator.last_name}",
            chair_email="finance.chair@unc.edu",
        )
        session.add(c)
        session.flush()
        session.refresh(c)
        assert c.chair_senator is not None
        assert c.chair_senator.id == senator.id

    def test_committee_is_active_default_true(self, session):
        c = Committee(
            name="C",
            description="D",
            chair_name="CN",
            chair_email="ce@unc.edu",
        )
        session.add(c)
        session.flush()
        assert c.is_active is True

    def test_committee_repr(self):
        c = Committee(name="Finance", description="D", chair_name="C", chair_email="c@c.com")
        assert "Finance" in repr(c)


# ===========================================================================
# CommitteeMembership model (M2M)
# ===========================================================================


class TestCommitteeMembershipModel:
    """Tests for CommitteeMembership many-to-many relationship."""

    def test_create_membership(self, session, senator, committee):
        m = CommitteeMembership(
            senator_id=senator.id,
            committee_id=committee.id,
            role="Member",
        )
        session.add(m)
        session.flush()
        assert m.id is not None

    def test_membership_default_role_is_member(self, session, senator, committee):
        m = CommitteeMembership(senator_id=senator.id, committee_id=committee.id)
        session.add(m)
        session.flush()
        assert m.role == "Member"

    def test_senator_relationship_on_membership(self, session, senator, committee):
        """CommitteeMembership.senator resolves to the Senator instance."""
        m = CommitteeMembership(senator_id=senator.id, committee_id=committee.id, role="Member")
        session.add(m)
        session.flush()
        session.refresh(m)
        assert m.senator.id == senator.id

    def test_committee_relationship_on_membership(self, session, senator, committee):
        """CommitteeMembership.committee resolves to the Committee instance."""
        m = CommitteeMembership(senator_id=senator.id, committee_id=committee.id, role="Vice Chair")
        session.add(m)
        session.flush()
        session.refresh(m)
        assert m.committee.id == committee.id

    def test_committee_memberships_back_reference(self, session, senator, committee):
        """Committee.memberships contains the created membership."""
        m = CommitteeMembership(senator_id=senator.id, committee_id=committee.id, role="Member")
        session.add(m)
        session.flush()
        session.refresh(committee)
        assert any(mem.id == m.id for mem in committee.memberships)

    def test_composite_unique_constraint_prevents_duplicate(self, session, senator, committee):
        """A senator cannot be assigned to the same committee twice."""
        m1 = CommitteeMembership(senator_id=senator.id, committee_id=committee.id, role="Member")
        m2 = CommitteeMembership(senator_id=senator.id, committee_id=committee.id, role="Vice Chair")
        session.add(m1)
        session.flush()
        session.add(m2)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_same_senator_different_committees_allowed(self, session, senator):
        """A senator may belong to multiple different committees."""
        c1 = Committee(name="C1", description="D", chair_name="N", chair_email="e@e.com")
        c2 = Committee(name="C2", description="D", chair_name="N", chair_email="e@e.com")
        session.add_all([c1, c2])
        session.flush()

        m1 = CommitteeMembership(senator_id=senator.id, committee_id=c1.id, role="Member")
        m2 = CommitteeMembership(senator_id=senator.id, committee_id=c2.id, role="Member")
        session.add_all([m1, m2])
        session.flush()  # should not raise
        assert m1.id != m2.id

    def test_membership_repr(self, senator, committee):
        m = CommitteeMembership(senator_id=1, committee_id=2, role="Chair")
        assert "1" in repr(m)
        assert "Chair" in repr(m)


# ===========================================================================
# Staff model
# ===========================================================================


class TestStaffModel:
    """Tests for the Staff model."""

    def test_create_staff(self, session):
        s = Staff(
            first_name="Alice",
            last_name="Nguyen",
            title="Chief of Staff",
            email="alice@unc.edu",
            display_order=1,
            is_active=True,
        )
        session.add(s)
        session.flush()
        assert s.id is not None

    def test_staff_photo_url_is_nullable(self, session):
        s = Staff(
            first_name="Bob",
            last_name="Smith",
            title="Advisor",
            email="bob@unc.edu",
            display_order=2,
        )
        session.add(s)
        session.flush()
        assert s.photo_url is None

    def test_staff_is_active_default_true(self, session):
        s = Staff(
            first_name="Carol",
            last_name="Jones",
            title="Intern",
            email="carol@unc.edu",
            display_order=3,
        )
        session.add(s)
        session.flush()
        assert s.is_active is True

    def test_staff_display_order_default_zero(self, session):
        s = Staff(
            first_name="Dan",
            last_name="Lee",
            title="Clerk",
            email="dan@unc.edu",
        )
        session.add(s)
        session.flush()
        assert s.display_order == 0

    def test_staff_repr(self):
        s = Staff(first_name="Alice", last_name="Nguyen", title="T", email="e@e.com", display_order=1)
        assert "Alice" in repr(s)
        assert "Nguyen" in repr(s)


# ===========================================================================
# StaticPageContent model
# ===========================================================================


class TestStaticPageContentModel:
    """Tests for the StaticPageContent model."""

    def test_create_static_page(self, session, admin):
        page = StaticPageContent(
            page_slug="powers-of-senate",
            title="Powers of the Senate",
            body="<p>The senate holds powers including...</p>",
            last_edited_by=admin.id,
        )
        session.add(page)
        session.flush()
        assert page.id is not None

    def test_page_slug_unique_constraint(self, session, admin):
        """Two pages with identical slugs must raise an IntegrityError."""
        p1 = StaticPageContent(
            page_slug="how-a-bill-becomes-law",
            title="How a Bill Becomes a Law",
            body="Body 1.",
            last_edited_by=admin.id,
        )
        p2 = StaticPageContent(
            page_slug="how-a-bill-becomes-law",
            title="Duplicate Page",
            body="Body 2.",
            last_edited_by=admin.id,
        )
        session.add(p1)
        session.flush()
        session.add(p2)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_multiple_different_slugs_allowed(self, session, admin):
        """Multiple pages with unique slugs must all be created."""
        slugs = ["public-disclosure", "how-to-apply", "budget-process"]
        for slug in slugs:
            page = StaticPageContent(
                page_slug=slug,
                title=slug.replace("-", " ").title(),
                body="Content.",
                last_edited_by=admin.id,
            )
            session.add(page)
        session.flush()  # should not raise

    def test_last_edited_by_relationship(self, session, admin):
        """StaticPageContent.editor resolves to the Admin instance."""
        page = StaticPageContent(
            page_slug="elections",
            title="Elections",
            body="Election info.",
            last_edited_by=admin.id,
        )
        session.add(page)
        session.flush()
        session.refresh(page)
        assert page.editor.id == admin.id

    def test_updated_at_auto_updates(self, session, admin):
        """updated_at must change when the row is updated via the ORM."""
        page = StaticPageContent(
            page_slug="senate-rules",
            title="Senate Rules",
            body="Original content.",
            last_edited_by=admin.id,
        )
        session.add(page)
        session.flush()

        old_date = datetime(2020, 6, 1)
        session.execute(
            update(StaticPageContent)
            .where(StaticPageContent.id == page.id)
            .values(updated_at=old_date)
        )
        session.refresh(page)
        assert page.updated_at == old_date

        page.title = "Senate Rules (Updated)"
        session.flush()
        session.refresh(page)
        assert page.updated_at > old_date

    def test_static_page_repr(self):
        p = StaticPageContent(page_slug="test-slug", title="T", body="B", last_edited_by=1)
        assert "test-slug" in repr(p)


# ===========================================================================
# AppConfig model
# ===========================================================================


class TestAppConfigModel:
    """Tests for the AppConfig model."""

    def test_create_app_config(self, session, admin):
        cfg = AppConfig(
            key="staffer_app_open",
            value="false",
            updated_by=admin.id,
        )
        session.add(cfg)
        session.flush()
        assert cfg.id is not None

    def test_key_unique_constraint(self, session, admin):
        """Two AppConfig rows with the same key must raise an IntegrityError."""
        cfg1 = AppConfig(key="finance_hearing_active", value="true", updated_by=admin.id)
        cfg2 = AppConfig(key="finance_hearing_active", value="false", updated_by=admin.id)
        session.add(cfg1)
        session.flush()
        session.add(cfg2)
        with pytest.raises(IntegrityError):
            session.flush()

    def test_multiple_distinct_keys_allowed(self, session, admin):
        """Multiple AppConfig rows with distinct keys must all be created."""
        keys = ["staffer_app_open", "finance_hearing_active", "maintenance_mode"]
        for key in keys:
            cfg = AppConfig(key=key, value="false", updated_by=admin.id)
            session.add(cfg)
        session.flush()  # should not raise

    def test_updated_by_relationship(self, session, admin):
        """AppConfig.updater resolves to the Admin instance."""
        cfg = AppConfig(key="some_toggle", value="true", updated_by=admin.id)
        session.add(cfg)
        session.flush()
        session.refresh(cfg)
        assert cfg.updater.id == admin.id

    def test_updated_at_auto_updates(self, session, admin):
        """updated_at must change when the row is updated via the ORM."""
        cfg = AppConfig(key="show_budget_viz", value="true", updated_by=admin.id)
        session.add(cfg)
        session.flush()

        old_date = datetime(2020, 3, 15)
        session.execute(
            update(AppConfig).where(AppConfig.id == cfg.id).values(updated_at=old_date)
        )
        session.refresh(cfg)
        assert cfg.updated_at == old_date

        cfg.value = "false"
        session.flush()
        session.refresh(cfg)
        assert cfg.updated_at > old_date

    def test_app_config_repr(self):
        cfg = AppConfig(key="my_key", value="my_value", updated_by=1)
        assert "my_key" in repr(cfg)
        assert "my_value" in repr(cfg)
