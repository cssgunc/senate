"""Default editable static page content and backfill helpers."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from textwrap import dedent

from sqlalchemy.orm import Session

from app.models.Admin import Admin
from app.models.cms import StaticPageContent


@dataclass(frozen=True)
class StaticPageDefault:
    slug: str
    title: str
    body: str


def _body(html: str) -> str:
    return dedent(html).strip()


STATIC_PAGE_DEFAULTS: tuple[StaticPageDefault, ...] = (
    StaticPageDefault(
        slug="senate-rules",
        title="Senate Rules",
        body=_body(
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
            """
        ),
    ),
    StaticPageDefault(
        slug="public-disclosure",
        title="Public Disclosure",
        body=_body(
            """
            <p>The Senate strives to be a transparent and accessible institution. The full records of the Senate, dating back to the 99th Senate (2017), may be found in this <a href="https://drive.google.com/drive/folders/1xmWhZ5MLD9OQEMFmc5JbGLu1XZQwJqGa?usp=drive_link">Google Drive</a> folder. Older records may be available at the Wilson Library Student Government Collection, or, in some cases, in a physical binder in the Speaker's office.</p>

            <p>If you need to request public records from the Senate, you may contact the Speaker at speaker@unc.edu.</p>
            """
        ),
    ),
    StaticPageDefault(
        slug="powers-of-senate",
        title="Powers of the Senate",
        body=_body(
            """
            <p>At UNC, the Senate is granted sweeping powers over the operations of Student Government. In fact, the Constitution grants the Senate the power to &quot;make all laws necessary and proper to promote the general welfare of the Undergraduate Student Body&quot;. Because this is Student Government, however, this broad mandate is more often limited by practical reality than by the barriers of constitutionality.</p>

            <p>The activities of the Senate can be broadly divided into three categories: advocacy, oversight, and law.</p>

            <h3>Law</h3>
            <p>The power of the Senate to engage in lawmaking and policymaking is the most governmental of its duties. As the legislative branch of Student Government, the Senate frequently amends student law to promote student interests. Notable examples of the Senate exercising its lawmaking power include the <a href="https://docs.google.com/document/d/14-lAbjXt9h8QQT-HfCb9EPm5Kgnxen_nHA3vQcuXE2o/edit?usp=sharing">FlowForward Nationalization Act</a>, which brought FlowForward, a student group that provided free menstrual products in campus bathrooms, under the umbrella of student government and the <a href="https://docs.google.com/document/d/1snCd1nMuYoV7cr7F2C2ceSZXTBpzHTVK9t5RDytwxXU/edit?usp=sharing">Inspector General Act</a>, which established a position empowered to file lawsuits in student court against members of student government on behalf of the student body. Lawmaking is the most impactful way by which the Senate can directly serve students on campus.</p>

            <h3>Advocacy</h3>
            <p>For aspects of the student experience that student government cannot directly impact, the Senate turns to advocacy. Results are less immediate and foolproof than lawmaking, but advocacy allows students to see their voices hear on the administration level. Major pieces of advocacy legislation include <a href="https://docs.google.com/document/d/1ckaYdBQ3Nx9HqcJfVdppSbqS88FYnaiHiuHeDhvFaJM/edit?usp=sharing">USR 107-119</a>, which successfully effected the return of tabletop napkin dispensers to dining halls after their removal over the summer of 2025 and <a href="https://docs.google.com/document/d/1lJSYqLjzzK2JzTrozet36Ld1hRJXIpu9JRLNwg3J7bQ/edit">USR 107-168</a>, which called for the installation of urinal dividers in the campus bathrooms that lack them. Resolutions that address quality-of-life issues are frequently successful and bring about change that would traditionally be out of reach of student law.</p>

            <h3>Oversight</h3>
            <p>Student government at UNC is a large institution, with its members numbering in the hundreds. For this reason, it is vital that the Senate ensures that all parts of the massive structure of student government are functioning properly. The Constitution grants the Senate with the power to confirm or reject appointments made by executive branch officials, including the Vice President, Treasurer, Justices of the Supreme Court, and Board of Elections Members. The Senate also maintains a Permanent Select Committee on Government Oversight, which ensures that the many parts of student government follow legal and ethical standards. As a last-case option, the Senate retains the sole power of impeachment to remove officials that act against the interests of the student body.</p>
            """
        ),
    ),
    StaticPageDefault(
        slug="how-a-bill-becomes-law",
        title="How a Bill Becomes a Law",
        body=_body(
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
            """
        ),
    ),
    StaticPageDefault(
        slug="elections",
        title="Elections for Senate",
        body=_body(
            """
            <p>Senate elections are typically held twice a year by the UNC Board of Elections. Senators serve one-year terms, unless they were elected during a special election. General elections for Senate are held at the same time as the election for Student Body President in the spring, while special elections are typically held in the middle of the fall semester.</p>

            <p>Senators are elected using two methods: districts and proportional seats. Two thirds of Senate seats are allocated to five academic discipline-based majors. To run for these seats, a candidate must collect fifty signatures from students in their district to appear on the ballot, then win a multi-winner election. One third of Senate seats are allocated to party lists, where groups of candidates with a collective interest or ideology may run together. Seats are allocated based on the proportion of the vote each group of candidates gets. For example, a group that earned 65% of the vote would be allocated 65% of the seats.</p>

            <p>Interested in running for Senate? Election dates are typically posted on the <a href="https://elections.unc.edu">Board of Elections' website</a>. It may also be helpful to contact the BOE directly at boe@unc.edu.</p>
            """
        ),
    ),
    StaticPageDefault(
        slug="staffer-application",
        title="Applying to be a Senate Staffer",
        body=_body(
            """
            <p>Staffers allow the Senate to operate smoothly and efficiently. Staffing roles range across a wide array of disciplines, from social media and communications to direct involvement in the oversight and finance processes.</p>

            <p>Staffing applications are currently closed, but will open in August 2026 for new staffers. For more information on staffing the Senate, you may contact Senate Chief of Staff Kripa Bhat at <a href="mailto:kbhat@unc.edu">kbhat@unc.edu</a>.</p>
            """
        ),
    ),
    StaticPageDefault(
        slug="how-to-apply",
        title="How to Apply for Funding",
        body="Student organizations can submit applications, supporting documents, and appeals through the funding portal.",
    ),
    StaticPageDefault(
        slug="budget-process",
        title="Budget Process Overview",
        body="The budget process includes request intake, finance hearings, committee recommendations, and senate approval.",
    ),
)

STATIC_PAGE_DEFAULTS_BY_SLUG = {page.slug: page for page in STATIC_PAGE_DEFAULTS}


def iter_static_page_defaults(slugs: Iterable[str] | None = None) -> tuple[StaticPageDefault, ...]:
    if slugs is None:
        return STATIC_PAGE_DEFAULTS
    return tuple(
        STATIC_PAGE_DEFAULTS_BY_SLUG[slug]
        for slug in slugs
        if slug in STATIC_PAGE_DEFAULTS_BY_SLUG
    )


def ensure_default_static_pages(
    db: Session,
    *,
    editor: Admin | None = None,
    slugs: Iterable[str] | None = None,
    commit: bool = False,
) -> int:
    """Insert missing configured static pages without overwriting edited content."""

    defaults = iter_static_page_defaults(slugs)
    if not defaults:
        return 0

    target_slugs = [page.slug for page in defaults]
    existing_slugs = {
        slug
        for (slug,) in db.query(StaticPageContent.page_slug)
        .filter(StaticPageContent.page_slug.in_(target_slugs))
        .all()
    }
    missing_pages = [page for page in defaults if page.slug not in existing_slugs]
    if not missing_pages:
        return 0

    editor_id = editor.id if editor is not None else None
    if editor_id is None:
        first_admin = db.query(Admin).order_by(Admin.id).first()
        if first_admin is None:
            return 0
        editor_id = first_admin.id

    db.add_all(
        StaticPageContent(
            page_slug=page.slug,
            title=page.title,
            body=page.body,
            last_edited_by=editor_id,
        )
        for page in missing_pages
    )

    if commit:
        db.commit()
    else:
        db.flush()

    return len(missing_pages)
