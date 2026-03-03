from datetime import date, datetime, time

from app.schemas import (
    AccountDTO,
    BudgetDataDTO,
    CalendarEventDTO,
    CarouselSlideDTO,
    CommitteeAssignmentDTO,
    CommitteeDTO,
    DistrictDTO,
    FinanceHearingConfigDTO,
    FinanceHearingDateDTO,
    LeadershipDTO,
    LegislationActionDTO,
    LegislationDTO,
    NewsDTO,
    SenatorDTO,
    StaffDTO,
    StaticPageDTO,
)

# ------------------------
# Test CommitteeDTO
# ------------------------
def test_committee_dto_serialization():
    committee_assignment = CommitteeAssignmentDTO(
        committee_id=1,
        committee_name="Finance",
        role="Member"
    )

    senator = SenatorDTO(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        district_id=100,
        is_active=True,
        session_number=2026,
        committees=[committee_assignment]
    )

    committee = CommitteeDTO(
        id=10,
        name="Finance",
        description="Finance Committee",
        chair_name="Jane Chair",
        chair_email="chair@example.com",
        members=[senator],
        is_active=True
    )

    data = committee.model_dump()
    assert data["id"] == 10
    assert data["members"][0]["first_name"] == "John"


# ------------------------
# Test NewsDTO with computed field
# ------------------------
def test_news_dto_computed_author():
    admin = AccountDTO(
        id=1,
        email="user@example.com",
        pid="pid123",
        first_name="Mock",
        last_name="Admin",
        role="admin"
    )

    news = NewsDTO(
        id=1,
        title="News Title",
        summary="Summary",
        body="Body",
        image_url=None,
        date_published=datetime(2026, 3, 3, 10, 0),
        date_last_edited=datetime(2026, 3, 3, 11, 0),
        admin=admin
    )

    data = news.model_dump()
    assert data["author_name"] == "Mock Admin"


# ------------------------
# Test LeadershipDTO
# ------------------------
def test_leadership_dto():
    leadership = LeadershipDTO(
        id=1,
        title="Governor",
        first_name="Bob",
        last_name="Leader",
        email="bob@example.com",
        photo_url=None,
        session_number=2026,
        is_current=True
    )

    data = leadership.model_dump()
    assert data["title"] == "Governor"
    assert data["is_current"] is True


# ------------------------
# Test LegislationDTO
# ------------------------
def test_legislation_dto():
    action = LegislationActionDTO(
        id=1,
        action_date=date(2026, 1, 1),
        description="Introduced",
        action_type="Bill Introduction"
    )

    legislation = LegislationDTO(
        id=1,
        title="Bill A",
        bill_number="A123",
        session_number=2026,
        sponsor_name="John Sponsor",
        summary="Summary",
        full_text="Full text",
        status="Active",
        type="Bill",
        date_introduced=date(2026, 1, 1),
        date_last_action=date(2026, 1, 2),
        actions=[action]
    )

    data = legislation.model_dump()
    assert data["actions"][0]["description"] == "Introduced"


# ------------------------
# Test CarouselSlideDTO
# ------------------------
def test_carousel_slide_dto():
    slide = CarouselSlideDTO(
        id=1,
        image_url="https://example.com/image.png",
        overlay_text="Overlay",
        link_url="https://example.com",
        display_order=1,
        is_active=True
    )

    data = slide.model_dump()
    assert data["overlay_text"] == "Overlay"


# ------------------------
# Test Finance DTOs
# ------------------------
def test_finance_hearing_dtos():
    hearing_date = FinanceHearingDateDTO(
        id=1,
        hearing_date=date(2026, 3, 3),
        hearing_time=time(14, 0),
        location="Room 101",
        description="Budget Hearing",
        is_full=False
    )

    config = FinanceHearingConfigDTO(
        is_active=True,
        season_start=date(2026, 1, 1),
        season_end=date(2026, 12, 31),
        dates=[hearing_date]
    )

    data = config.model_dump()
    assert data["dates"][0]["location"] == "Room 101"


# ------------------------
# Test StaffDTO
# ------------------------
def test_staff_dto():
    staff = StaffDTO(
        id=1,
        first_name="Sally",
        last_name="Staff",
        title="Manager",
        email="sally@example.com",
        photo_url=None
    )

    data = staff.model_dump()
    assert data["title"] == "Manager"


# ------------------------
# Test DistrictDTO
# ------------------------
def test_district_dto():
    senator = SenatorDTO(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        district_id=100,
        is_active=True,
        session_number=2026,
        committees=[]
    )

    district = DistrictDTO(
        id=1,
        district_name="District 1",
        description=None,
        senator=[senator]
    )

    data = district.model_dump()
    assert data["senator"][0]["last_name"] == "Doe"


# ------------------------
# Test BudgetDataDTO recursive
# ------------------------
def test_budget_dto_recursive():
    child_budget = BudgetDataDTO(
        id=2,
        fiscal_year="2026",
        category="Subcategory",
        amount=100.0,
        description=None,
        children=[]
    )

    parent_budget = BudgetDataDTO(
        id=1,
        fiscal_year="2026",
        category="Main",
        amount=1000.0,
        description="Main budget",
        children=[child_budget]
    )

    data = parent_budget.model_dump()
    assert data["children"][0]["category"] == "Subcategory"


# ------------------------
# Test StaticPageDTO
# ------------------------
def test_static_page_dto():
    page = StaticPageDTO(
        id=1,
        page_slug="about",
        title="About Us",
        body="Content",
        updated_at=datetime.now()
    )

    data = page.model_dump()
    assert data["page_slug"] == "about"


# ------------------------
# Test AccountDTO
# ------------------------
def test_account_dto():
    account = AccountDTO(
        id=1,
        email="user@example.com",
        pid="pid123",
        first_name="User",
        last_name="Example",
        role="admin"
    )

    data = account.model_dump()
    assert data["role"] == "admin"

# ------------------------
# Test CalendarEventDTO
# ------------------------
def test_calendar_event_dto():
    event = CalendarEventDTO(
        id=1,
        title="Budget Meeting",
        description="Discuss budget allocations",
        start_datetime=datetime(2026, 3, 10, 9, 0),
        end_datetime=datetime(2026, 3, 10, 11, 0),
        location="Room 101",
        event_type="Hearing"
    )

    data = event.model_dump()
    assert data["title"] == "Budget Meeting"
    assert data["start_datetime"] == datetime(2026, 3, 10, 9, 0)
    assert data["event_type"] == "Hearing"
