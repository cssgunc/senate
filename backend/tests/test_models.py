"""Tests for SQL Alchemy models, explicitly Legislation, Events, Carousel, Finance, Budget"""

from datetime import date

# Import your models
from app.models import (
    Base,
    Legislation,
    LegislationAction,
    BudgetData
)

# Imports models
from app.models import BudgetData, Legislation, LegislationAction, Base

# ------------------------------
# Pytest Fixtures
# ------------------------------

@pytest.fixture(scope="module")
def engine():
    # In-memory SQLite database
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.rollback()
    sess.close()


# ------------------------------
# Table existence tests
# ------------------------------

def test_tables_exist(engine, tables):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    expected_tables = [
        "legislation",
        "legislation_action",
        "calendar_event",
        "carousel_slide",
        "finance_hearing_config",
        "finance_hearing_date",
        "budget_data"
    ]
    print(table_names)
    for table in expected_tables:
        assert table in table_names, f"Table {table} should exist"


# ------------------------------
# Legislation → LegislationAction one-to-many relationship
# ------------------------------

def test_legislation_action_relationship(session):
    # Create legislation
    leg = Legislation(
        title="Test Bill",
        bill_number=101,
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
    session.commit()

    # Create actions
    action1 = LegislationAction(
        legislation_id=leg.id,
        action_date=date(2026, 1, 3),
        description="First Action",
        action_type="Committee",
        display_order=1
    )
    action2 = LegislationAction(
        legislation_id=leg.id,
        action_date=date(2026, 1, 4),
        description="Second Action",
        action_type="Vote",
        display_order=2
    )
    session.add_all([action1, action2])
    session.commit()

    # Verify actions are linked
    actions = session.query(LegislationAction).filter_by(legislation_id=leg.id).all()
    assert len(actions) == 2
    assert actions[0].description == "First Action"
    assert actions[1].description == "Second Action"


# ------------------------------
# BudgetData self-referential FK
# ------------------------------

def test_budgetdata_self_reference(session):
    parent = BudgetData(
        fiscal_year=2026,
        category="Parent Category",
        amount=1000.00,
        display_order=1,
        updated_by=1
    )
    session.add(parent)
    session.commit()

    child = BudgetData(
        fiscal_year=2026,
        category="Child Category",
        amount=500.00,
        parent_category_id=parent.id,
        display_order=2,
        updated_by=1
    )
    session.add(child)
    session.commit()

    # Fetchs child and verify parent link
    fetched_child = session.query(BudgetData).filter_by(id=child.id).one()
    assert fetched_child.parent_category_id == parent.id

    # Using ORM relationship, if defined
    if hasattr(fetched_child, "parent_category"):
        assert fetched_child.parent_category.category == "Parent Category"
        # Tests reverse backref
        assert fetched_child in parent.subcategories
