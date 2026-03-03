"""Tests for remaining models: Legislation, LegislationAction, CalendarEvent,
CarouselSlide, FinanceHearingConfig, FinanceHearingDate, BudgetData.

Uses the shared conftest.py engine/session fixtures (in-memory SQLite).
Metadata-inspection tests need no session; CRUD tests use the transactional session.
"""

from datetime import date, datetime, time

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError

from app.models import (
    BudgetData,
    CalendarEvent,
    CarouselSlide,
    FinanceHearingConfig,
    FinanceHearingDate,
    Legislation,
    LegislationAction,
)

# ---------------------------------------------------------------------------
# Helpers (same pattern as test_core_models)
# ---------------------------------------------------------------------------


def get_columns(model):
    """Return a dict of {column_name: column_object} for a model."""
    return {c.name: c for c in model.__table__.columns}


def get_fk_target_tables(model):
    """Return a set of target table names referenced by FKs in the model."""
    targets = set()
    for col in model.__table__.columns:
        for fk in col.foreign_keys:
            targets.add(fk.column.table.name)
    return targets


# ===========================================================================
# Table existence
# ===========================================================================


class TestTableExistence:
    """All seven tables must be present in the database."""

    def test_all_other_tables_exist(self, engine):
        inspector = sa_inspect(engine)
        tables = inspector.get_table_names()
        expected = [
            "legislation",
            "legislation_action",
            "calendar_event",
            "carousel_slide",
            "finance_hearing_config",
            "finance_hearing_date",
            "budget_data",
        ]
        for table in expected:
            assert table in tables, f"Table {table!r} should exist"


# ===========================================================================
# Legislation
# ===========================================================================


class TestLegislationModel:
    """Tests for the Legislation model."""

    def test_table_name(self):
        assert Legislation.__tablename__ == "legislation"

    def test_columns_exist(self):
        cols = get_columns(Legislation)
        expected = {
            "id",
            "title",
            "bill_number",
            "session_number",
            "sponsor_id",
            "sponsor_name",
            "summary",
            "full_text",
            "status",
            "type",
            "date_introduced",
            "date_last_action",
            "created_at",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_bill_number_is_string(self):
        cols = get_columns(Legislation)
        assert cols["bill_number"].type.length == 50

    def test_sponsor_id_fk_to_senator(self):
        assert "senator" in get_fk_target_tables(Legislation)

    def test_sponsor_id_nullable(self):
        cols = get_columns(Legislation)
        assert cols["sponsor_id"].nullable is True

    def test_summary_not_nullable(self):
        cols = get_columns(Legislation)
        assert cols["summary"].nullable is False

    def test_full_text_not_nullable(self):
        cols = get_columns(Legislation)
        assert cols["full_text"].nullable is False

    def test_date_last_action_not_nullable(self):
        cols = get_columns(Legislation)
        assert cols["date_last_action"].nullable is False

    def test_updated_at_has_onupdate(self):
        cols = get_columns(Legislation)
        assert cols["updated_at"].onupdate is not None

    def test_create_legislation(self, session, senator):
        leg = Legislation(
            title="Test Resolution",
            bill_number="SR-200",
            session_number=2,
            sponsor_id=senator.id,
            sponsor_name="Senator Alpha",
            summary="A test resolution summary",
            full_text="Full text of the resolution",
            status="Introduced",
            type="Resolution",
            date_introduced=date(2026, 3, 1),
            date_last_action=date(2026, 3, 5),
        )
        session.add(leg)
        session.flush()

        assert leg.id is not None
        assert leg.title == "Test Resolution"
        assert leg.bill_number == "SR-200"
        assert leg.session_number == 2
        assert leg.sponsor_name == "Senator Alpha"
        assert leg.status == "Introduced"
        assert leg.type == "Resolution"
        assert leg.date_introduced == date(2026, 3, 1)
        assert leg.date_last_action == date(2026, 3, 5)

    def test_legislation_sponsor_id_nullable_in_practice(self, session):
        """Legislation can be created without a sponsor FK."""
        leg = Legislation(
            title="Anonymous Bill",
            bill_number="SB-999",
            session_number=1,
            sponsor_id=None,
            sponsor_name="External Sponsor",
            summary="Summary",
            full_text="Full text",
            status="Introduced",
            type="Bill",
            date_introduced=date(2026, 1, 1),
            date_last_action=date(2026, 1, 2),
        )
        session.add(leg)
        session.flush()
        assert leg.sponsor_id is None

    def test_legislation_created_at_default(self, session):
        leg = Legislation(
            title="Timestamp Bill",
            bill_number="SB-201",
            session_number=1,
            sponsor_name="Senator Beta",
            summary="Summary",
            full_text="Text",
            status="Passed",
            type="Bill",
            date_introduced=date(2026, 1, 1),
            date_last_action=date(2026, 1, 5),
        )
        session.add(leg)
        session.flush()
        session.refresh(leg)
        assert leg.created_at is not None

    def test_legislation_updated_at_auto_updates(self, session):
        leg = Legislation(
            title="Update Test",
            bill_number="SB-202",
            session_number=1,
            sponsor_name="Senator Gamma",
            summary="Summary",
            full_text="Text",
            status="Introduced",
            type="Bill",
            date_introduced=date(2026, 2, 1),
            date_last_action=date(2026, 2, 3),
        )
        session.add(leg)
        session.flush()

        old_date = datetime(2020, 1, 1)
        session.execute(
            update(Legislation).where(Legislation.id == leg.id).values(updated_at=old_date)
        )
        session.refresh(leg)
        assert leg.updated_at == old_date

        leg.title = "Updated Title"
        session.flush()
        session.refresh(leg)
        assert leg.updated_at > old_date


# ===========================================================================
# LegislationAction
# ===========================================================================


class TestLegislationActionModel:
    """Tests for the LegislationAction model."""

    def test_table_name(self):
        assert LegislationAction.__tablename__ == "legislation_action"

    def test_columns_exist(self):
        cols = get_columns(LegislationAction)
        expected = {
            "id",
            "legislation_id",
            "action_date",
            "description",
            "action_type",
            "display_order",
        }
        assert expected == set(cols.keys())

    def test_fk_to_legislation(self):
        assert "legislation" in get_fk_target_tables(LegislationAction)

    def test_all_columns_not_nullable(self):
        cols = get_columns(LegislationAction)
        for name, col in cols.items():
            if name == "id":
                continue
            assert col.nullable is False, f"{name} should be NOT NULL"

    def test_create_action_linked_to_legislation(self, session):
        leg = Legislation(
            title="Action Parent Bill",
            bill_number="SB-301",
            session_number=1,
            sponsor_name="Senator Test",
            summary="Summary",
            full_text="Full Text",
            status="Passed",
            type="Bill",
            date_introduced=date(2026, 1, 1),
            date_last_action=date(2026, 1, 2),
        )
        session.add(leg)
        session.flush()

        action = LegislationAction(
            legislation_id=leg.id,
            action_date=date(2026, 1, 3),
            description="First Reading",
            action_type="Committee",
            display_order=1,
        )
        session.add(action)
        session.flush()

        assert action.id is not None
        assert action.legislation_id == leg.id

    def test_multiple_actions_for_one_legislation(self, session):
        leg = Legislation(
            title="Multi-Action Bill",
            bill_number="SB-302",
            session_number=1,
            sponsor_name="Senator Multi",
            summary="Summary",
            full_text="Full Text",
            status="Passed",
            type="Bill",
            date_introduced=date(2026, 1, 1),
            date_last_action=date(2026, 1, 4),
        )
        session.add(leg)
        session.flush()

        for i in range(1, 4):
            action = LegislationAction(
                legislation_id=leg.id,
                action_date=date(2026, 1, i),
                description=f"Action {i}",
                action_type="Floor",
                display_order=i,
            )
            session.add(action)
        session.flush()

        actions = (
            session.query(LegislationAction)
            .filter_by(legislation_id=leg.id)
            .order_by(LegislationAction.display_order)
            .all()
        )
        assert len(actions) == 3
        assert [a.display_order for a in actions] == [1, 2, 3]
        assert [a.description for a in actions] == ["Action 1", "Action 2", "Action 3"]

    def test_action_requires_legislation_fk(self, session):
        """An action without a valid legislation_id must be rejected by FK constraint."""
        action = LegislationAction(
            legislation_id=999999,
            action_date=date(2026, 5, 1),
            description="Orphan Action",
            action_type="Vote",
            display_order=1,
        )
        session.add(action)
        with pytest.raises(IntegrityError):
            session.flush()


# ===========================================================================
# CalendarEvent
# ===========================================================================


class TestCalendarEventModel:
    """Tests for the CalendarEvent model."""

    def test_table_name(self):
        assert CalendarEvent.__tablename__ == "calendar_event"

    def test_columns_exist(self):
        cols = get_columns(CalendarEvent)
        expected = {
            "id",
            "title",
            "description",
            "start_datetime",
            "end_datetime",
            "location",
            "event_type",
            "is_published",
            "created_by",
        }
        assert expected == set(cols.keys())

    def test_fk_to_admin(self):
        assert "admin" in get_fk_target_tables(CalendarEvent)

    def test_created_by_not_nullable(self):
        cols = get_columns(CalendarEvent)
        assert cols["created_by"].nullable is False

    def test_description_nullable(self):
        cols = get_columns(CalendarEvent)
        assert cols["description"].nullable is True

    def test_location_nullable(self):
        cols = get_columns(CalendarEvent)
        assert cols["location"].nullable is True

    def test_create_calendar_event(self, session, admin):
        event = CalendarEvent(
            title="Senate Meeting",
            description="Weekly senate meeting",
            start_datetime=datetime(2026, 6, 15, 18, 0, 0),
            end_datetime=datetime(2026, 6, 15, 20, 0, 0),
            location="Union Room 3209",
            event_type="Meeting",
            is_published=True,
            created_by=admin.id,
        )
        session.add(event)
        session.flush()

        assert event.id is not None
        assert event.title == "Senate Meeting"
        assert event.description == "Weekly senate meeting"
        assert event.location == "Union Room 3209"
        assert event.event_type == "Meeting"
        assert event.is_published is True

    def test_calendar_event_nullable_fields(self, session, admin):
        event = CalendarEvent(
            title="Minimal Event",
            start_datetime=datetime(2026, 8, 1, 10, 0, 0),
            end_datetime=datetime(2026, 8, 1, 11, 0, 0),
            event_type="Other",
            is_published=False,
            created_by=admin.id,
        )
        session.add(event)
        session.flush()

        assert event.description is None
        assert event.location is None

    def test_calendar_event_requires_created_by(self, session):
        """created_by is NOT NULL — omitting it must fail."""
        event = CalendarEvent(
            title="No Creator",
            start_datetime=datetime(2026, 9, 1, 14, 0, 0),
            end_datetime=datetime(2026, 9, 1, 15, 0, 0),
            event_type="Meeting",
            is_published=False,
            created_by=None,
        )
        session.add(event)
        with pytest.raises(IntegrityError):
            session.flush()


# ===========================================================================
# CarouselSlide
# ===========================================================================


class TestCarouselSlideModel:
    """Tests for the CarouselSlide model."""

    def test_table_name(self):
        assert CarouselSlide.__tablename__ == "carousel_slide"

    def test_columns_exist(self):
        cols = get_columns(CarouselSlide)
        expected = {
            "id",
            "image_url",
            "overlay_text",
            "link_url",
            "display_order",
            "is_active",
        }
        assert expected == set(cols.keys())

    def test_image_url_not_nullable(self):
        cols = get_columns(CarouselSlide)
        assert cols["image_url"].nullable is False

    def test_overlay_text_nullable(self):
        cols = get_columns(CarouselSlide)
        assert cols["overlay_text"].nullable is True

    def test_link_url_nullable(self):
        cols = get_columns(CarouselSlide)
        assert cols["link_url"].nullable is True

    def test_create_carousel_slide(self, session):
        slide = CarouselSlide(
            image_url="https://example.com/welcome.jpg",
            overlay_text="Welcome to UNC Senate",
            link_url="https://senate.unc.edu",
            display_order=1,
            is_active=True,
        )
        session.add(slide)
        session.flush()

        assert slide.id is not None
        assert slide.image_url == "https://example.com/welcome.jpg"
        assert slide.overlay_text == "Welcome to UNC Senate"
        assert slide.link_url == "https://senate.unc.edu"
        assert slide.display_order == 1
        assert slide.is_active is True

    def test_carousel_slide_nullable_fields(self, session):
        slide = CarouselSlide(
            image_url="https://example.com/img.jpg",
            display_order=20,
            is_active=True,
        )
        session.add(slide)
        session.flush()

        assert slide.overlay_text is None
        assert slide.link_url is None

    def test_carousel_slide_ordering(self, session):
        for i in [30, 10, 20]:
            slide = CarouselSlide(
                image_url=f"https://example.com/slide{i}.jpg",
                display_order=i,
                is_active=True,
            )
            session.add(slide)
        session.flush()

        slides = (
            session.query(CarouselSlide)
            .filter(CarouselSlide.display_order.in_([10, 20, 30]))
            .order_by(CarouselSlide.display_order)
            .all()
        )
        assert [s.display_order for s in slides] == [10, 20, 30]

    def test_carousel_slide_inactive(self, session):
        slide = CarouselSlide(
            image_url="https://example.com/old.jpg",
            display_order=99,
            is_active=False,
        )
        session.add(slide)
        session.flush()
        assert slide.is_active is False


# ===========================================================================
# FinanceHearingConfig
# ===========================================================================


class TestFinanceHearingConfigModel:
    """Tests for the FinanceHearingConfig model."""

    def test_table_name(self):
        assert FinanceHearingConfig.__tablename__ == "finance_hearing_config"

    def test_columns_exist(self):
        cols = get_columns(FinanceHearingConfig)
        expected = {
            "id",
            "is_active",
            "season_start",
            "season_end",
            "updated_by",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_fk_to_admin(self):
        assert "admin" in get_fk_target_tables(FinanceHearingConfig)

    def test_updated_by_not_nullable(self):
        cols = get_columns(FinanceHearingConfig)
        assert cols["updated_by"].nullable is False

    def test_season_start_nullable(self):
        cols = get_columns(FinanceHearingConfig)
        assert cols["season_start"].nullable is True

    def test_season_end_nullable(self):
        cols = get_columns(FinanceHearingConfig)
        assert cols["season_end"].nullable is True

    def test_is_active_default_true(self):
        cols = get_columns(FinanceHearingConfig)
        assert cols["is_active"].default is not None

    def test_updated_at_has_onupdate(self):
        cols = get_columns(FinanceHearingConfig)
        assert cols["updated_at"].onupdate is not None

    def test_create_finance_hearing_config(self, session, admin):
        config = FinanceHearingConfig(
            is_active=True,
            season_start=date(2026, 9, 1),
            season_end=date(2026, 12, 15),
            updated_by=admin.id,
        )
        session.add(config)
        session.flush()

        assert config.id is not None
        assert config.is_active is True
        assert config.season_start == date(2026, 9, 1)
        assert config.season_end == date(2026, 12, 15)

    def test_finance_hearing_config_nullable_dates(self, session, admin):
        config = FinanceHearingConfig(
            is_active=False,
            updated_by=admin.id,
        )
        session.add(config)
        session.flush()

        assert config.season_start is None
        assert config.season_end is None

    def test_finance_hearing_config_updated_at_default(self, session, admin):
        config = FinanceHearingConfig(
            is_active=True,
            updated_by=admin.id,
        )
        session.add(config)
        session.flush()
        session.refresh(config)
        assert config.updated_at is not None

    def test_finance_hearing_config_updated_at_auto_updates(self, session, admin):
        config = FinanceHearingConfig(
            is_active=True,
            updated_by=admin.id,
        )
        session.add(config)
        session.flush()

        old_date = datetime(2020, 1, 1)
        session.execute(
            update(FinanceHearingConfig)
            .where(FinanceHearingConfig.id == config.id)
            .values(updated_at=old_date)
        )
        session.refresh(config)
        assert config.updated_at == old_date

        config.is_active = False
        session.flush()
        session.refresh(config)
        assert config.updated_at > old_date


# ===========================================================================
# FinanceHearingDate
# ===========================================================================


class TestFinanceHearingDateModel:
    """Tests for the FinanceHearingDate model."""

    def test_table_name(self):
        assert FinanceHearingDate.__tablename__ == "finance_hearing_date"

    def test_columns_exist(self):
        cols = get_columns(FinanceHearingDate)
        expected = {
            "id",
            "hearing_date",
            "hearing_time",
            "location",
            "description",
            "is_full",
        }
        assert expected == set(cols.keys())

    def test_location_nullable(self):
        cols = get_columns(FinanceHearingDate)
        assert cols["location"].nullable is True

    def test_description_nullable(self):
        cols = get_columns(FinanceHearingDate)
        assert cols["description"].nullable is True

    def test_is_full_default_false(self):
        cols = get_columns(FinanceHearingDate)
        assert cols["is_full"].default is not None

    def test_hearing_date_not_nullable(self):
        cols = get_columns(FinanceHearingDate)
        assert cols["hearing_date"].nullable is False

    def test_hearing_time_not_nullable(self):
        cols = get_columns(FinanceHearingDate)
        assert cols["hearing_time"].nullable is False

    def test_create_finance_hearing_date(self, session):
        hd = FinanceHearingDate(
            hearing_date=date(2026, 9, 15),
            hearing_time=time(10, 0),
            location="Union Room 3201",
            description="Fall finance hearing session 1",
            is_full=False,
        )
        session.add(hd)
        session.flush()

        assert hd.id is not None
        assert hd.hearing_date == date(2026, 9, 15)
        assert hd.hearing_time == time(10, 0)
        assert hd.location == "Union Room 3201"
        assert hd.description == "Fall finance hearing session 1"
        assert hd.is_full is False

    def test_finance_hearing_date_nullable_fields(self, session):
        hd = FinanceHearingDate(
            hearing_date=date(2026, 10, 1),
            hearing_time=time(14, 30),
            is_full=False,
        )
        session.add(hd)
        session.flush()

        assert hd.location is None
        assert hd.description is None

    def test_finance_hearing_date_is_full(self, session):
        hd = FinanceHearingDate(
            hearing_date=date(2026, 11, 1),
            hearing_time=time(9, 0),
            is_full=True,
        )
        session.add(hd)
        session.flush()
        assert hd.is_full is True

    def test_multiple_hearing_dates(self, session):
        dates = []
        for day in [5, 10, 15]:
            hd = FinanceHearingDate(
                hearing_date=date(2026, 12, day),
                hearing_time=time(10, 0),
                is_full=False,
            )
            dates.append(hd)
        session.add_all(dates)
        session.flush()

        fetched = (
            session.query(FinanceHearingDate)
            .filter(FinanceHearingDate.hearing_date >= date(2026, 12, 1))
            .order_by(FinanceHearingDate.hearing_date)
            .all()
        )
        assert len(fetched) == 3
        assert fetched[0].hearing_date == date(2026, 12, 5)
        assert fetched[2].hearing_date == date(2026, 12, 15)


# ===========================================================================
# BudgetData
# ===========================================================================


class TestBudgetDataModel:
    """Tests for the BudgetData model."""

    def test_table_name(self):
        assert BudgetData.__tablename__ == "budget_data"

    def test_columns_exist(self):
        cols = get_columns(BudgetData)
        expected = {
            "id",
            "fiscal_year",
            "category",
            "amount",
            "description",
            "parent_category_id",
            "display_order",
            "updated_by",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_fiscal_year_is_string(self):
        cols = get_columns(BudgetData)
        assert cols["fiscal_year"].type.length == 20

    def test_fk_to_admin(self):
        assert "admin" in get_fk_target_tables(BudgetData)

    def test_self_referential_fk(self):
        assert "budget_data" in get_fk_target_tables(BudgetData)

    def test_description_nullable(self):
        cols = get_columns(BudgetData)
        assert cols["description"].nullable is True

    def test_parent_category_id_nullable(self):
        cols = get_columns(BudgetData)
        assert cols["parent_category_id"].nullable is True

    def test_updated_by_not_nullable(self):
        cols = get_columns(BudgetData)
        assert cols["updated_by"].nullable is False

    def test_updated_at_has_onupdate(self):
        cols = get_columns(BudgetData)
        assert cols["updated_at"].onupdate is not None

    def test_create_budget_data(self, session, admin):
        budget = BudgetData(
            fiscal_year="2025-2026",
            category="Student Organizations",
            amount=50000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()

        assert budget.id is not None
        assert budget.fiscal_year == "2025-2026"
        assert budget.category == "Student Organizations"
        assert float(budget.amount) == 50000.00
        assert budget.display_order == 1

    def test_budgetdata_self_reference(self, session, admin):
        parent = BudgetData(
            fiscal_year="2026-2027",
            category="Parent Category",
            amount=1000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(parent)
        session.flush()

        child = BudgetData(
            fiscal_year="2026-2027",
            category="Child Category",
            amount=500.00,
            parent_category_id=parent.id,
            display_order=2,
            updated_by=admin.id,
        )
        session.add(child)
        session.flush()

        fetched_child = session.query(BudgetData).filter_by(id=child.id).one()
        assert fetched_child.parent_category_id == parent.id

    def test_budgetdata_multiple_children(self, session, admin):
        parent = BudgetData(
            fiscal_year="2027-2028",
            category="Operations",
            amount=100000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(parent)
        session.flush()

        for i, name in enumerate(["Salaries", "Equipment", "Travel"], start=1):
            child = BudgetData(
                fiscal_year="2027-2028",
                category=name,
                amount=10000.00 * i,
                parent_category_id=parent.id,
                display_order=i + 1,
                updated_by=admin.id,
            )
            session.add(child)
        session.flush()

        children = (
            session.query(BudgetData)
            .filter_by(parent_category_id=parent.id)
            .order_by(BudgetData.display_order)
            .all()
        )
        assert len(children) == 3
        assert [c.category for c in children] == ["Salaries", "Equipment", "Travel"]

    def test_budgetdata_nullable_parent(self, session, admin):
        budget = BudgetData(
            fiscal_year="2028-2029",
            category="Top Level",
            amount=200000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()
        assert budget.parent_category_id is None

    def test_budgetdata_nullable_description(self, session, admin):
        budget = BudgetData(
            fiscal_year="2029-2030",
            category="No Description",
            amount=5000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()
        assert budget.description is None

    def test_budgetdata_with_description(self, session, admin):
        budget = BudgetData(
            fiscal_year="2030-2031",
            category="Described",
            amount=7500.00,
            description="This budget line has a description.",
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()
        assert budget.description == "This budget line has a description."

    def test_budgetdata_amount_precision(self, session, admin):
        budget = BudgetData(
            fiscal_year="2031-2032",
            category="Precise Budget",
            amount=12345.67,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()
        assert abs(float(budget.amount) - 12345.67) < 0.01

    def test_budgetdata_updated_at_default(self, session, admin):
        budget = BudgetData(
            fiscal_year="2032-2033",
            category="Timestamp Budget",
            amount=999.99,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()
        session.refresh(budget)
        assert budget.updated_at is not None

    def test_budgetdata_updated_at_auto_updates(self, session, admin):
        budget = BudgetData(
            fiscal_year="2033-2034",
            category="Update Test Budget",
            amount=1000.00,
            display_order=1,
            updated_by=admin.id,
        )
        session.add(budget)
        session.flush()

        old_date = datetime(2020, 1, 1)
        session.execute(
            update(BudgetData).where(BudgetData.id == budget.id).values(updated_at=old_date)
        )
        session.refresh(budget)
        assert budget.updated_at == old_date

        budget.category = "Updated Category"
        session.flush()
        session.refresh(budget)
        assert budget.updated_at > old_date


# ===========================================================================
# __init__.py exports
# ===========================================================================


def test_all_other_models_exported():
    """All seven 'other' models must be in app.models.__all__."""
    from app import models

    expected = {
        "Legislation",
        "LegislationAction",
        "CalendarEvent",
        "CarouselSlide",
        "FinanceHearingConfig",
        "FinanceHearingDate",
        "BudgetData",
    }
    assert expected.issubset(set(models.__all__))
