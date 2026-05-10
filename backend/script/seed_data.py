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
            "senate-rules",
            "Senate Rules",
            """
            <p>While the Senate is formally established by the Constitution and governed by the Undergraduate General Statutes, procedure within the body follows a set of rules passed at the first meeting of each year. These rules govern everything from giving public comment to impeachment. The current form of the Senate's rules dates back to 2023, when they were substantially rewritten by Speaker Emeritus Christopher McClanahan, who then served as Chair of the Rules and Judiciary Committee.</p>

            <p>While the vast majority of the 55-page rules document has to do with the internal pathways for legislation and motions that may be made by senators, there are some provisions that are relevant to anyone who wishes to show up at a senate meeting.</p>

            <p><strong>Rule 18</strong>, in particular, governs the <strong>Public Comment Period</strong> of a Senate meeting. This is the period during which any student may address the Senate for up to two minutes at a time. It should be noted that because the Public Comment Period occurs after reports of the officers, it only typically occurs more than 30 minutes into the meeting.</p>

            <p>Relatedly, <strong>Rule 11</strong> sets the agenda of a regular meeting and establishes the officers that must address the Senate each time it meets. The order of speaking is as follows:</p>
            <ol>
              <li>Speaker of the Senate</li>
              <li>Speaker Pro Tempore of the Senate</li>
              <li>Chair of the Finance Committee</li>
              <li>Chair of the R&amp;J Committee</li>
              <li>Chair of the Student Affairs Committee</li>
              <li>Chair of the Ethics Committee</li>
              <li>Chair of the Government Oversight Committee</li>
              <li>Student Body President</li>
              <li>Undergraduate Vice President</li>
              <li>Undergraduate Treasurer</li>
              <li>Undergraduate Secretary</li>
              <li>Undergraduate Chief of the Cabinet</li>
              <li>Chief Legal Officer</li>
            </ol>

            <p>If you want to stay updated on the goings-on of student government, listening to officer reports is a great way to start. Information on the roles of these officers can be found on the <a href="/senators/leadership">Senate Leadership page</a>.</p>

            <p><strong>Rule 61</strong> also establishes an important method of involvement in the proceedings of the Senate. This rule allows any student to sign onto a piece of legislation, expressing your personal support for the item as it goes through the legislative process. If you're curious about what kind of legislation the Senate will be considering at the next meeting, check out our <a href="/legislation/search">legislative database</a>.</p>

            <p>A full version of the Senate rules can be found below.</p>

            <p><a href="https://docs.google.com/document/d/1keVFE8M5w_a1H4Uz85CbVBt79TyjQxO_fUhy1wC-F2E/edit?usp=sharing" data-variant="button">View Full Senate Rules</a></p>
            """,
        ),
        (
            "public-disclosure",
            "Public Disclosure",
            """
            <p>The Senate strives to be a transparent and accessible institution. The full records of the Senate, dating back to the 99th Senate (2017), may be found in this <a href="https://drive.google.com/drive/folders/1xmWhZ5MLD9OQEMFmc5JbGLu1XZQwJqGa?usp=drive_link">Google Drive</a> folder. Older records may be available at the Wilson Library Student Government Collection, or, in some cases, in a physical binder in the Speaker's office.</p>

            <p>If you need to request public records from the Senate, you may contact the Speaker at speaker@unc.edu.</p>
            """,
        ),
        (
            "powers-of-senate",
            "Powers of the Senate",
            """
            <p>At UNC, the Senate is granted sweeping powers over the operations of Student Government. In fact, the Constitution grants the Senate the power to &quot;make all laws necessary and proper to promote the general welfare of the Undergraduate Student Body&quot;. Because this is Student Government, however, this broad mandate is more often limited by practical reality than by the barriers of constitutionality.</p>

            <p>The activities of the Senate can be broadly divided into three categories: advocacy, oversight, and law.</p>

            <h3>Law</h3>
            <p>The power of the Senate to engage in lawmaking and policymaking is the most governmental of its duties. As the legislative branch of Student Government, the Senate frequently amends student law to promote student interests. Notable examples of the Senate exercising its lawmaking power include the <a href="https://docs.google.com/document/d/14-lAbjXt9h8QQT-HfCb9EPm5Kgnxen_nHA3vQcuXE2o/edit?usp=sharing">FlowForward Nationalization Act</a>, which brought FlowForward, a student group that provided free menstrual products in campus bathrooms, under the umbrella of student government and the <a href="https://docs.google.com/document/d/1snCd1nMuYoV7cr7F2C2ceSZXTBpzHTVK9t5RDytwxXU/edit?usp=sharing">Inspector General Act</a>, which established a position empowered to file lawsuits in student court against members of student government on behalf of the student body. Lawmaking is the most impactful way by which the Senate can directly serve students on campus.</p>

            <h3>Advocacy</h3>
            <p>For aspects of the student experience that student government cannot directly impact, the Senate turns to advocacy. Results are less immediate and foolproof than lawmaking, but advocacy allows students to see their voices hear on the administration level. Major pieces of advocacy legislation include <a href="https://docs.google.com/document/d/1ckaYdBQ3Nx9HqcJfVdppSbqS88FYnaiHiuHeDhvFaJM/edit?usp=sharing">USR 107-119</a>, which successfully effected the return of tabletop napkin dispensers to dining halls after their removal over the summer of 2025 and <a href="https://docs.google.com/document/d/1lJSYqLjzzK2JzTrozet36Ld1hRJXIpu9JRLNwg3J7bQ/edit">USR 107-168</a>, which called for the installation of urinal dividers in the campus bathrooms that lack them. Resolutions that address quality-of-life issues are frequently successful and bring about change that would traditionally be out of reach of student law.</p>

            <h3>Oversight</h3>
            <p>Student government at UNC is a large institution, with its members numbering in the hundreds. For this reason, it is vital that the Senate ensures that all parts of the massive structure of student government are functioning properly. The Constitution grants the Senate with the power to confirm or reject appointments made by executive branch officials, including the Vice President, Treasurer, Justices of the Supreme Court, and Board of Elections Members. The Senate also maintains a Permanent Select Committee on Government Oversight, which ensures that the many parts of student government follow legal and ethical standards. As a last-case option, the Senate retains the sole power of impeachment to remove officials that act against the interests of the student body.</p>
            """,
        ),
        (
            "how-a-bill-becomes-law",
            "How a Bill Becomes a Law",
            """
            <p>Each meeting of the Senate, senators pass legislation, from changing individual words in the Senate's internal rules to creating entire new agencies to provide vital needs to students. These pieces of legislation have to make it from someone's ideas to force of law somehow, which is where the Senate's standing rules come in. These standing rules govern how a bill or resolution comes into effect. To understand the process, it is important to draw a distinction between a bill and a resolution.</p>

            <p>While the actual definition is more complicated, a bill typically changes the law, while a resolution does anything else. As a vast oversimplification, a bill can be thought to make a rule, while a resolution can be thought to make something happen.</p>

            <h2>How Things Typically Work</h2>

            <p>The Senate's procedure is complex, but most bills and resolutions follow a standard procedure, as outlined below.</p>

            <ol>
              <li><strong>An Idea</strong>: Every piece of legislation starts as a concept championed by a Senator. This idea is drafted as that legislation, and during the drafting period, Senators and other students may sign on as cosponsors and signatories respectively. Cosponsoring and signing are procedures that allow other individuals to express their support for legislation as it goes through the legislative process.</li>
              <li><strong>Submission and Referral</strong>: Once the piece of legislation is finished, it is presented to the Speaker, who refers it to a Senate Committee, with its topic determining the committee it is referred to. If a Senate meeting is soon, however, the legislation may instead be referred to the Committee of the Whole, meaning it is functionally presented to the full Senate immediately upon presentation to the Speaker.</li>
              <li><strong>Committee</strong>: After referral, a committee will hear the legislation. Committees are select groups of senators who specialize on certain topics. There are four ways by which a piece of legislation can leave committee. A broadly popular piece of legislation will usually be "referred favorably", allowing it to pass the full senate without debate. A controversial piece of legislation will be "referred without prejudice", meaning it will be heard by the full Senate with debate. A broadly unpopular resolution will typically be "referred unfavorably", allowing it to fail on the Senate floor without debate. The final option, which does not required referral by the Committee, is a discharge petition. If five senators agree that the Senate should consider a piece of legislation, it can bypass committee and be heard directly on the Senate floor.</li>
              <li><strong>The Senate Floor</strong>: Following committee, legislation makes it to the Senate floor, where all Senators have the right to debate. On the floor, legislation receives final votes, determining whether it will pass or fail.</li>
              <li><strong>The President's Desk</strong>: Bills, unlike resolutions, are delivered to the President to sign or veto. Only upon the signature of the President (or a veto override) do they enter into law.</li>
            </ol>

            <h2>Edge Cases</h2>

            <p>While the procedure outlined above is how legislation typically passes the Senate, there are several other routes taken by specific types of legislation. These routes are outlined below.</p>

            <ol>
              <li><strong>Joint Legislation</strong>: Legislation that is "joint" (i.e. it affects both graduate and undergraduate students) requires an extra step to pass into law. When a joint bill or resolution passes the Senate, it is passed to the Joint Governance Council instead of the President. The Joint Governance Council, or JGC, is the oft-overlooked "third legislature" of student government, and its voting membership consists of four members of the Undergraduate Senate and four members of the Graduate Senate. In order for a joint piece of legislation to pass the JGC, it must pass by two-thirds and have the support of at least one member of each constituency.</li>
              <li><strong>Impeachments</strong>: Impeachments bypass the committee process entirely, instead being presented directly to the floor of the Senate. Impeachment of an officer of Student Government requires a majority of the Senate to pass. Following the passage of an impeachment resolution, the Chief Justice of the Student Supreme Court schedules an impeachment trial, wherein Senators weigh whether to remove the impeached officer. If the officer is joint, such as a Justice or Member of the Board or Elections, the conviction must be upheld by the JGC.</li>
              <li><strong>Vetoed Legislation</strong>: When a bill is vetoed, it is returned to the Senate for a veto override. If the Senate still wishes to pass the bill after it is vetoed, then it must be passed by two-thirds, after which it becomes law.</li>
              <li><strong>Amendments to the Constitution</strong>: Amendments to the Constitution follow the typical procedure for legislation, but with additional steps. First, amendments must pass the Senate by two-thirds. If the amendment is joint, it must also be passed by the Graduate Senate before moving to the next step. Following its passage by both Senates, it is sent to a public referendum, where it must pass and receive at least 2.5% turnout. Only after being passed by the student body may it enter into effect.</li>
            </ol>
            """,
        ),
        (
            "elections",
            "Elections for Senate",
            """
            <p>Senate elections are typically held twice a year by the UNC Board of Elections. Senators serve one-year terms, unless they were elected during a special election. General elections for Senate are held at the same time as the election for Student Body President in the spring, while special elections are typically held in the middle of the fall semester.</p>

            <p>Senators are elected using two methods: districts and proportional seats. Two thirds of Senate seats are allocated to five academic discipline-based majors. To run for these seats, a candidate must collect fifty signatures from students in their district to appear on the ballot, then win a multi-winner election. One third of Senate seats are allocated to party lists, where groups of candidates with a collective interest or ideology may run together. Seats are allocated based on the proportion of the vote each group of candidates gets. For example, a group that earned 65% of the vote would be allocated 65% of the seats.</p>

            <p>Interested in running for Senate? Election dates are typically posted on the <a href="https://elections.unc.edu">Board of Elections' website</a>. It may also be helpful to contact the BOE directly at boe@unc.edu.</p>
            """,
        ),
        (
            "staffer-application",
            "Applying to be a Senate Staffer",
            """
            <p>Staffers allow the Senate to operate smoothly and efficiently. Staffing roles range across a wide array of disciplines, from social media and communications to direct involvement in the oversight and finance processes.</p>

            <p>Staffing applications are currently closed, but will open in August 2026 for new staffers. For more information on staffing the Senate, you may contact Senate Chief of Staff Kripa Bhat at <a href="mailto:kbhat@unc.edu">kbhat@unc.edu</a>.</p>
            """,
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
