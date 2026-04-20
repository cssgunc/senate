"""Seed the development database with realistic UNC Senate sample data.

Usage:
    python -m script.seed_data

This script is idempotent: it clears existing application data and re-seeds
all tables with deterministic sample records.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    Admin,
    AdminSections,
    AppConfig,
    BudgetData,
    CalendarEvent,
    CarouselSlide,
    Committee,
    CommitteeMembership,
    District,
    DistrictMapping,
    FinanceHearingConfig,
    FinanceHearingDate,
    Leadership,
    Legislation,
    LegislationAction,
    News,
    Sections,
    Senator,
    Staff,
    StaticPageContent,
)

CURRENT_SESSION = 111

NEWS_IMAGE_PATHS = [
    "/image-temp/apply_image.jpeg",
    "/image-temp/undergrad_senate.jpeg",
    "/image-temp/governer_image.jpeg",
]

PROFILE_IMAGE_PATHS = [
    "/image-temp/profile_3.jpg",
    "/image-temp/profile_4.jpg",
    "/image-temp/all_profiles.jpg",
    "/image-temp/profile_1.jpeg",
    "/image-temp/profile_2.jpg",
]

CAROUSEL_IMAGE_PATHS = [
    "/image-temp/governer_image.jpeg",
    "/image-temp/meetings_area.jpg",
    "/image-temp/undergrad_senate_2.jpeg",
    "/image-temp/apply_image.jpeg",
]


def clear_existing_data(db: Session) -> None:
    """Delete all seeded entities in foreign-key safe order."""
    db.query(CommitteeMembership).delete(synchronize_session=False)
    db.query(LegislationAction).delete(synchronize_session=False)
    db.query(FinanceHearingDate).delete(synchronize_session=False)

    # Self-referential FK requires children to be removed before parents.
    db.query(BudgetData).filter(BudgetData.parent_category_id.is_not(None)).delete(
        synchronize_session=False
    )
    db.query(BudgetData).filter(BudgetData.parent_category_id.is_(None)).delete(
        synchronize_session=False
    )

    db.query(CalendarEvent).delete(synchronize_session=False)
    db.query(CarouselSlide).delete(synchronize_session=False)
    db.query(News).delete(synchronize_session=False)
    db.query(StaticPageContent).delete(synchronize_session=False)
    db.query(AppConfig).delete(synchronize_session=False)
    db.query(FinanceHearingConfig).delete(synchronize_session=False)
    db.query(Leadership).delete(synchronize_session=False)
    db.query(Committee).delete(synchronize_session=False)
    db.query(Legislation).delete(synchronize_session=False)
    db.query(Senator).delete(synchronize_session=False)
    db.query(DistrictMapping).delete(synchronize_session=False)
    db.query(District).delete(synchronize_session=False)
    db.query(Staff).delete(synchronize_session=False)
    db.query(AdminSections).delete(synchronize_session=False)
    db.query(Sections).delete(synchronize_session=False)
    db.query(Admin).delete(synchronize_session=False)
    db.flush()


def seed_admins(db: Session) -> list[Admin]:
    admins = [
        Admin(
            email="alex.thompson@unc.edu",
            first_name="Alex",
            last_name="Thompson",
            pid="720114563",
            role="admin",
        ),
        Admin(
            email="morgan.lee@unc.edu",
            first_name="Morgan",
            last_name="Lee",
            pid="681905244",
            role="admin",
        ),
        Admin(
            email="jordan.rivera@unc.edu",
            first_name="Jordan",
            last_name="Rivera",
            pid="538227190",
            role="staff",
        ),
    ]
    db.add_all(admins)
    db.flush()
    return admins


def seed_sections(db: Session, admins: list[Admin]) -> None:
    section_names = [
        "news",
        "legislation",
        "senators",
        "committees",
        "finance",
        "static-pages",
    ]
    sections = [Sections(name=name) for name in section_names]
    db.add_all(sections)
    db.flush()

    admin_sections = [
        AdminSections(section_id=section.id, admin_id=admins[0].id) for section in sections
    ]
    admin_sections.extend(
        [
            AdminSections(section_id=sections[0].id, admin_id=admins[1].id),
            AdminSections(section_id=sections[1].id, admin_id=admins[1].id),
            AdminSections(section_id=sections[4].id, admin_id=admins[2].id),
        ]
    )
    db.add_all(admin_sections)


def seed_districts(db: Session) -> list[District]:
    district_rows = [
        (
            "North Campus",
            "Represents residents primarily in North Campus and nearby residence halls.",
            "NORTH-CAMPUS",
        ),
        (
            "South Campus",
            "Represents South Campus residence halls and apartment communities.",
            "SOUTH-CAMPUS",
        ),
        (
            "Granville Towers",
            "Represents students living in and around Granville Towers.",
            "GRANVILLE",
        ),
        (
            "Off-Campus",
            "Represents undergraduates living off campus in Chapel Hill and Carrboro.",
            "OFF-CAMPUS",
        ),
        (
            "Transfer & Commuter",
            "Represents transfer and commuter undergraduate student populations.",
            "TRANSFER-COMMUTER",
        ),
    ]

    districts: list[District] = []
    for district_name, description, mapping_value in district_rows:
        district = District(district_name=district_name, description=description)
        db.add(district)
        db.flush()
        districts.append(district)
        db.add(DistrictMapping(district_id=district.id, mapping_value=mapping_value))

    return districts


def seed_senators(db: Session, districts: list[District]) -> list[Senator]:
    senator_rows = [
        ("Avery", "Brooks"),
        ("Riley", "Nguyen"),
        ("Cameron", "Patel"),
        ("Skyler", "Davis"),
        ("Quinn", "Johnson"),
        ("Parker", "Kim"),
        ("Reese", "Martinez"),
        ("Jordan", "Murphy"),
        ("Hayden", "Carter"),
        ("Rowan", "Mitchell"),
        ("Sawyer", "Brown"),
        ("Logan", "Walker"),
        ("Emerson", "Hall"),
        ("Dakota", "Young"),
        ("Taylor", "Allen"),
    ]

    senators: list[Senator] = []
    for idx, (first_name, last_name) in enumerate(senator_rows, start=1):
        district = districts[(idx - 1) % len(districts)]
        profile_image = PROFILE_IMAGE_PATHS[(idx - 1) % len(PROFILE_IMAGE_PATHS)]
        senator = Senator(
            first_name=first_name,
            last_name=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}@unc.edu",
            headshot_url=profile_image,
            district=district.id,
            is_active=True,
            session_number=CURRENT_SESSION,
        )
        db.add(senator)
        senators.append(senator)

    db.flush()
    return senators


def seed_leadership(db: Session, senators: list[Senator]) -> None:
    titles = [
        "Speaker",
        "Speaker Pro Tempore",
        "Clerk",
        "Treasurer",
        "Parliamentarian",
        "Sergeant at Arms",
    ]

    rows = []
    for idx, title in enumerate(titles):
        senator = senators[idx]
        rows.append(
            Leadership(
                senator_id=senator.id,
                title=title,
                first_name=senator.first_name,
                last_name=senator.last_name,
                email=senator.email,
                headshot_url=senator.headshot_url,
                is_active=True,
                session_number=CURRENT_SESSION,
            )
        )

    db.add_all(rows)


def seed_committees(db: Session, senators: list[Senator]) -> list[Committee]:
    committee_specs = [
        (
            "Finance",
            "Reviews funding requests and recommends allocations to student organizations.",
            senators[0],
        ),
        (
            "Rules and Judiciary",
            "Interprets bylaws, election procedures, and constitutional questions.",
            senators[1],
        ),
        (
            "Student Affairs",
            "Focuses on undergraduate student life, wellness, and campus climate.",
            senators[2],
        ),
        (
            "Academic Affairs",
            "Advances academic policy priorities, advising quality, and classroom resources.",
            senators[3],
        ),
    ]

    committees: list[Committee] = []
    for name, description, chair in committee_specs:
        committee = Committee(
            name=name,
            description=description,
            chair_senator_id=chair.id,
            chair_name=f"{chair.first_name} {chair.last_name}",
            chair_email=chair.email,
            is_active=True,
        )
        db.add(committee)
        committees.append(committee)

    db.flush()

    memberships: list[CommitteeMembership] = []
    for idx, committee in enumerate(committees):
        start = idx * 3
        selected = senators[start : start + 4]
        for jdx, senator in enumerate(selected):
            role = "Chair" if jdx == 0 else ("Vice Chair" if jdx == 1 else "Member")
            memberships.append(
                CommitteeMembership(
                    senator_id=senator.id,
                    committee_id=committee.id,
                    role=role,
                )
            )

    db.add_all(memberships)
    return committees


def seed_news(db: Session, admins: list[Admin]) -> None:
    now = datetime.now(timezone.utc)
    rows: list[News] = []

    for idx in range(10):
        author = admins[idx % len(admins)]
        published = idx < 7
        image_path = NEWS_IMAGE_PATHS[idx % len(NEWS_IMAGE_PATHS)]
        rows.append(
            News(
                title=f"Senate Weekly Update #{idx + 1}",
                summary="Highlights from Undergraduate Senate deliberations and upcoming campus actions.",
                body=(
                    "The Undergraduate Senate met to discuss student priorities including "
                    "academic support, transportation, and organization funding. "
                    "This update summarizes key motions and next steps."
                ),
                image_url=image_path,
                author_id=author.id,
                date_published=now - timedelta(days=idx * 3),
                is_published=published,
            )
        )

    db.add_all(rows)


def seed_legislation(db: Session, senators: list[Senator]) -> None:
    today = date.today()
    statuses = [
        "Introduced",
        "In Committee",
        "Passed",
        "Failed",
        "In Committee",
        "Passed",
        "Introduced",
        "In Committee",
    ]
    types = [
        "Bill",
        "Resolution",
        "Bill",
        "Bill",
        "Resolution",
        "Bill",
        "Bill",
        "Resolution",
    ]
    titles = [
        "Peer Tutoring Expansion Act",
        "Resolution on Extended Library Hours",
        "Campus Safety Lighting Improvement Act",
        "Sustainable Events Procurement Bill",
        "Resolution Supporting Mental Health Days",
        "Student Org Funding Transparency Act",
        "Dining Hall Late-Night Pilot Bill",
        "Resolution on Open Textbook Access",
    ]

    legislation_rows: list[Legislation] = []
    for idx in range(8):
        introduced = today - timedelta(days=50 - (idx * 5))
        last_action = introduced + timedelta(days=idx % 4 + 2)
        sponsor = senators[idx]
        legislation = Legislation(
            title=titles[idx],
            bill_number=f"S{CURRENT_SESSION}-{100 + idx}",
            session_number=CURRENT_SESSION,
            sponsor_id=sponsor.id,
            sponsor_name=f"{sponsor.first_name} {sponsor.last_name}",
            summary="Legislation focused on practical improvements for undergraduate life at UNC.",
            full_text=(
                "Section 1. Purpose. This legislation establishes a targeted initiative to "
                "improve undergraduate student outcomes. Section 2. Implementation. Relevant "
                "campus partners shall coordinate with Undergraduate Senate committees."
            ),
            status=statuses[idx],
            type=types[idx],
            date_introduced=introduced,
            date_last_action=last_action,
        )
        db.add(legislation)
        legislation_rows.append(legislation)

    db.flush()

    action_templates = [
        [
            ("Filed with Clerk", "Filing"),
            ("First reading completed", "Reading"),
        ],
        [
            ("Filed with Clerk", "Filing"),
            ("Referred to committee", "Referral"),
            ("Committee hearing held", "Hearing"),
        ],
        [
            ("Filed with Clerk", "Filing"),
            ("Committee recommendation: pass", "Committee Vote"),
            ("Passed on floor vote", "Floor Vote"),
            ("Signed by Speaker", "Signature"),
        ],
        [
            ("Filed with Clerk", "Filing"),
            ("Committee recommendation: fail", "Committee Vote"),
            ("Failed on floor vote", "Floor Vote"),
        ],
    ]

    actions: list[LegislationAction] = []
    for idx, legislation in enumerate(legislation_rows):
        template = action_templates[idx % len(action_templates)]
        for order, (description, action_type) in enumerate(template, start=1):
            actions.append(
                LegislationAction(
                    legislation_id=legislation.id,
                    action_date=legislation.date_introduced + timedelta(days=order),
                    description=description,
                    action_type=action_type,
                    display_order=order,
                )
            )

    db.add_all(actions)


def seed_calendar_events(db: Session, admins: list[Admin]) -> None:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    offsets = [-21, -14, -7, -2, 3, 7, 11, 16, 22, 28]

    rows = []
    for idx, day_offset in enumerate(offsets, start=1):
        start = now + timedelta(days=day_offset, hours=18 - now.hour)
        end = start + timedelta(hours=2)
        rows.append(
            CalendarEvent(
                title=f"Senate Event {idx}",
                description="Open meeting for undergraduate students and student organization representatives.",
                start_datetime=start,
                end_datetime=end,
                location="Student Union, Room 2420",
                event_type="Meeting" if idx % 3 else "Hearing",
                is_published=True,
                created_by=admins[0].id,
            )
        )

    db.add_all(rows)


def seed_carousel_slides(db: Session) -> None:
    slides = [
        CarouselSlide(
            image_url=CAROUSEL_IMAGE_PATHS[0],
            overlay_text="Your Voice in Student Government",
            link_url="/about/powers",
            display_order=1,
            is_active=True,
        ),
        CarouselSlide(
            image_url=CAROUSEL_IMAGE_PATHS[1],
            overlay_text="Funding Opportunities for Student Organizations",
            link_url="/funding",
            display_order=2,
            is_active=True,
        ),
        CarouselSlide(
            image_url=CAROUSEL_IMAGE_PATHS[2],
            overlay_text="Track Legislation in Real Time",
            link_url="/legislation/recent",
            display_order=3,
            is_active=True,
        ),
        CarouselSlide(
            image_url=CAROUSEL_IMAGE_PATHS[3],
            overlay_text="Explore Committee Work",
            link_url="/committees",
            display_order=4,
            is_active=True,
        ),
    ]
    db.add_all(slides)


def seed_finance_hearing_data(db: Session, admin: Admin) -> None:
    today = date.today()
    start = date(today.year, 9, 1)
    end = date(today.year + 1, 4, 30)

    db.add(
        FinanceHearingConfig(
            is_active=True,
            season_start=start,
            season_end=end,
            updated_by=admin.id,
        )
    )

    hearing_dates = [
        FinanceHearingDate(
            hearing_date=today + timedelta(days=10),
            hearing_time=time(17, 0),
            location="Frank Porter Graham Student Union, Room 3206",
            description="Student organization operating budget hearings.",
            is_full=False,
        ),
        FinanceHearingDate(
            hearing_date=today + timedelta(days=17),
            hearing_time=time(17, 30),
            location="Frank Porter Graham Student Union, Room 3206",
            description="Capital request hearings and Q&A.",
            is_full=False,
        ),
        FinanceHearingDate(
            hearing_date=today + timedelta(days=24),
            hearing_time=time(18, 0),
            location="Frank Porter Graham Student Union, Room 2420",
            description="Appeals and final finance committee recommendations.",
            is_full=False,
        ),
    ]
    db.add_all(hearing_dates)


def seed_staff(db: Session) -> None:
    staff_rows = [
        ("Mia", "Foster", "Chief of Staff", "mia.foster@unc.edu"),
        ("Noah", "Bailey", "Director of Communications", "noah.bailey@unc.edu"),
        ("Isla", "Reed", "Legislative Analyst", "isla.reed@unc.edu"),
        ("Ethan", "Price", "Finance Coordinator", "ethan.price@unc.edu"),
        ("Lila", "Woods", "Student Engagement Coordinator", "lila.woods@unc.edu"),
    ]

    rows = [
        Staff(
            first_name=first_name,
            last_name=last_name,
            title=title,
            email=email,
            photo_url=PROFILE_IMAGE_PATHS[(idx - 1) % len(PROFILE_IMAGE_PATHS)],
            display_order=idx,
            is_active=True,
        )
        for idx, (first_name, last_name, title, email) in enumerate(staff_rows, start=1)
    ]

    db.add_all(rows)


def seed_static_pages(db: Session, editor: Admin) -> None:
    pages = [
        (
            "powers",
            "Powers of the Senate",
            "The Undergraduate Senate approves budgets, oversees legislation, and advocates for student needs across UNC.",
        ),
        (
            "bill-process",
            "How a Bill Moves Through Senate",
            "Bills are filed with the Clerk, assigned to committee, and brought to the floor for debate and vote.",
        ),
        (
            "disclosure",
            "Legislation Public Disclosure",
            "Public records for active legislation, sponsor information, and action history are available here.",
        ),
        (
            "elections",
            "Undergraduate Senate Elections",
            "Election timelines, candidate requirements, and district details are published each semester.",
        ),
        (
            "how-to-apply",
            "How to Apply for Funding",
            "Student organizations can submit applications, supporting documents, and appeals through the funding portal.",
        ),
        (
            "budget-process",
            "Budget Process Overview",
            "The budget process includes request intake, finance hearings, committee recommendations, and senate approval.",
        ),
    ]

    rows = [
        StaticPageContent(
            page_slug=slug,
            title=title,
            body=body,
            last_edited_by=editor.id,
        )
        for slug, title, body in pages
    ]
    db.add_all(rows)


def seed_budget_data(db: Session, admin: Admin) -> None:
    fiscal_year = f"FY{date.today().year}-{date.today().year + 1}"

    top_level_specs = [
        (
            "Student Organization Allocations",
            Decimal("450000.00"),
            "Annual allocations for recognized student organizations.",
        ),
        ("Campus Programming", Decimal("220000.00"), "Large-scale campus events and traditions."),
        (
            "Wellness & Basic Needs",
            Decimal("180000.00"),
            "Mental health, food security, and wellbeing initiatives.",
        ),
        (
            "Academic Support Initiatives",
            Decimal("150000.00"),
            "Peer tutoring, academic coaching, and learning resources.",
        ),
        (
            "Operations & Administration",
            Decimal("95000.00"),
            "Administrative systems, staffing, and compliance costs.",
        ),
    ]

    top_level_rows: list[BudgetData] = []
    for idx, (category, amount, description) in enumerate(top_level_specs, start=1):
        row = BudgetData(
            fiscal_year=fiscal_year,
            category=category,
            amount=amount,
            description=description,
            parent_category_id=None,
            display_order=idx,
            updated_by=admin.id,
        )
        db.add(row)
        top_level_rows.append(row)

    db.flush()

    subcategories = [
        (0, "Large Requests", Decimal("260000.00"), "Requests above standard threshold."),
        (0, "Small Requests", Decimal("190000.00"), "Rapid-response and small grant requests."),
        (1, "Homecoming", Decimal("90000.00"), "Homecoming week programming and logistics."),
        (1, "Carolina Week", Decimal("130000.00"), "University-wide spring programming."),
        (
            2,
            "Mental Health Grants",
            Decimal("110000.00"),
            "Counseling and peer support initiatives.",
        ),
        (
            2,
            "Food Access Programs",
            Decimal("70000.00"),
            "Campus pantry and meal support initiatives.",
        ),
        (3, "Peer Tutoring", Decimal("85000.00"), "Department-linked tutoring programs."),
        (3, "Technology Access", Decimal("65000.00"), "Academic software and lending support."),
        (4, "Compliance & Audit", Decimal("45000.00"), "Required audit and compliance activities."),
        (
            4,
            "Platform Maintenance",
            Decimal("50000.00"),
            "Web systems, forms, and automation tools.",
        ),
    ]

    sub_rows: list[BudgetData] = []
    for idx, (parent_idx, category, amount, description) in enumerate(subcategories, start=1):
        sub_rows.append(
            BudgetData(
                fiscal_year=fiscal_year,
                category=category,
                amount=amount,
                description=description,
                parent_category_id=top_level_rows[parent_idx].id,
                display_order=100 + idx,
                updated_by=admin.id,
            )
        )

    db.add_all(sub_rows)


def seed_app_config(db: Session, admin: Admin) -> None:
    rows = [
        AppConfig(key="staffer_app_open", value="true", updated_by=admin.id),
        AppConfig(key="finance_hearing_active", value="true", updated_by=admin.id),
    ]
    db.add_all(rows)


def print_summary(db: Session) -> None:
    print("Seeding complete. Created:")
    print(f"  Admin accounts: {db.query(Admin).count()}")
    print(
        f"  Districts: {db.query(District).count()} (mappings: {db.query(DistrictMapping).count()})"
    )
    print(f"  Senators: {db.query(Senator).count()}")
    print(f"  Leadership positions: {db.query(Leadership).count()}")
    print(
        f"  Committees: {db.query(Committee).count()} (memberships: {db.query(CommitteeMembership).count()})"
    )
    print(f"  News articles: {db.query(News).count()}")
    print(
        f"  Legislation: {db.query(Legislation).count()} (actions: {db.query(LegislationAction).count()})"
    )
    print(f"  Calendar events: {db.query(CalendarEvent).count()}")
    print(f"  Carousel slides: {db.query(CarouselSlide).count()}")
    print(
        "  Finance hearing config/dates: "
        f"{db.query(FinanceHearingConfig).count()}/{db.query(FinanceHearingDate).count()}"
    )
    print(f"  Staff members: {db.query(Staff).count()}")
    print(f"  Static pages: {db.query(StaticPageContent).count()}")
    print(f"  Budget rows: {db.query(BudgetData).count()}")
    print(f"  App config entries: {db.query(AppConfig).count()}")


def run_seed() -> None:
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        clear_existing_data(db)

        print("Seeding sample data...")
        admins = seed_admins(db)
        seed_sections(db, admins)
        districts = seed_districts(db)
        senators = seed_senators(db, districts)
        seed_leadership(db, senators)
        seed_committees(db, senators)
        seed_news(db, admins)
        seed_legislation(db, senators)
        seed_calendar_events(db, admins)
        seed_carousel_slides(db)
        seed_finance_hearing_data(db, admins[0])
        seed_staff(db)
        seed_static_pages(db, admins[0])
        seed_budget_data(db, admins[0])
        seed_app_config(db, admins[0])

        db.commit()
        print_summary(db)
    except Exception as exc:
        db.rollback()
        print(f"Seeding failed: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Seeding Development Database")
    print("=" * 60)
    try:
        run_seed()
    except Exception:
        sys.exit(1)
    print("=" * 60)
    print("Seeding Finished")
    print("=" * 60)
