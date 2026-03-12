"""Integration tests for GET /api/legislation endpoints (ticket #35)."""

from datetime import date

from app.models.Legislation import Legislation
from app.models.LegislationAction import LegislationAction


def make_legislation(
    session: int = 1,
    title: str = "Test Bill",
    bill_number: str = "SB-001",
    summary: str = "A test summary",
    status: str = "Introduced",
    type: str = "Bill",
    sponsor_name: str = "Jane Doe",
    date_introduced: date = date(2025, 1, 1),
    date_last_action: date = date(2025, 1, 2),
    full_text: str = "Full text here.",
):
    return Legislation(
        session_number=session,
        title=title,
        bill_number=bill_number,
        summary=summary,
        status=status,
        type=type,
        sponsor_name=sponsor_name,
        date_introduced=date_introduced,
        date_last_action=date_last_action,
        full_text=full_text,
    )


# ---------------------------------------------------------------------------
# GET /api/legislation
# ---------------------------------------------------------------------------


def test_list_legislation_empty(integration_client):
    resp = integration_client.get("/api/legislation")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_legislation_defaults_to_current_session(integration_client, db_session):
    db_session.add(make_legislation(session=1, title="Old Bill"))
    db_session.add(make_legislation(session=2, title="New Bill"))
    db_session.commit()

    resp = integration_client.get("/api/legislation")
    assert resp.status_code == 200
    titles = [i["title"] for i in resp.json()["items"]]
    assert "New Bill" in titles
    assert "Old Bill" not in titles


def test_list_legislation_filter_by_session(integration_client, db_session):
    db_session.add(make_legislation(session=1, title="Old Bill"))
    db_session.add(make_legislation(session=2, title="New Bill"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?session=1")
    titles = [i["title"] for i in resp.json()["items"]]
    assert titles == ["Old Bill"]


def test_list_legislation_search_by_title(integration_client, db_session):
    db_session.add(make_legislation(title="Budget Reform Act"))
    db_session.add(make_legislation(title="Campus Safety Bill", bill_number="SB-002"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?search=budget")
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Budget Reform Act"
    assert "actions" not in items[0]


def test_list_legislation_search_by_bill_number(integration_client, db_session):
    db_session.add(make_legislation(bill_number="SR-099"))
    db_session.add(make_legislation(bill_number="SB-002", title="Other"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?search=SR-099")
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["bill_number"] == "SR-099"


def test_list_legislation_search_by_full_text(integration_client, db_session):
    db_session.add(make_legislation(full_text="Whereas the senate hereby resolves to fund clubs"))
    db_session.add(
        make_legislation(full_text="Unrelated content", bill_number="SB-002", title="Other")
    )
    db_session.commit()

    resp = integration_client.get("/api/legislation?search=fund+clubs")
    items = resp.json()["items"]
    assert len(items) == 1


def test_list_legislation_search_by_summary(integration_client, db_session):
    db_session.add(make_legislation(summary="Addresses parking violations on campus"))
    db_session.add(make_legislation(summary="Unrelated topic", bill_number="SB-002", title="Other"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?search=parking")
    items = resp.json()["items"]
    assert len(items) == 1


def test_list_legislation_filter_by_status(integration_client, db_session):
    db_session.add(make_legislation(status="Introduced"))
    db_session.add(make_legislation(status="Passed", bill_number="SB-002", title="Passed Bill"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?status=Passed")
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "Passed"


def test_list_legislation_filter_by_type(integration_client, db_session):
    db_session.add(make_legislation(type="Bill"))
    db_session.add(make_legislation(type="Nomination", bill_number="SB-002", title="Nomination"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?type=Nomination")
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["type"] == "Nomination"


def test_list_legislation_filter_by_sponsor(integration_client, db_session):
    db_session.add(make_legislation(sponsor_name="Alice Smith"))
    db_session.add(make_legislation(sponsor_name="Bob Jones", bill_number="SB-002", title="Other"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?sponsor=alice")
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["sponsor_name"] == "Alice Smith"


def test_list_legislation_combines_multiple_filters(integration_client, db_session):
    db_session.add(
        make_legislation(
            session=2,
            title="Campus Housing Funding Act",
            summary="Allocates new housing funds",
            status="Passed",
            type="Bill",
            sponsor_name="Alice Johnson",
        )
    )
    db_session.add(
        make_legislation(
            session=2,
            title="Campus Housing Funding Act",
            summary="Allocates new housing funds",
            status="Introduced",
            type="Bill",
            sponsor_name="Alice Johnson",
            bill_number="SB-002",
        )
    )
    db_session.add(
        make_legislation(
            session=1,
            title="Campus Housing Funding Act",
            summary="Allocates new housing funds",
            status="Passed",
            type="Bill",
            sponsor_name="Alice Johnson",
            bill_number="SB-003",
        )
    )
    db_session.commit()

    resp = integration_client.get(
        "/api/legislation?session=2&search=housing&status=Passed&type=Bill&sponsor=alice"
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "Passed"
    assert items[0]["session_number"] == 2


def test_list_legislation_pagination(integration_client, db_session):
    for i in range(5):
        db_session.add(make_legislation(bill_number=f"SB-{i:03}", title=f"Bill {i}"))
    db_session.commit()

    resp = integration_client.get("/api/legislation?page=1&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["limit"] == 2

    resp2 = integration_client.get("/api/legislation?page=3&limit=2")
    assert len(resp2.json()["items"]) == 1


# ---------------------------------------------------------------------------
# GET /api/legislation/{id}
# ---------------------------------------------------------------------------


def test_get_legislation_detail(integration_client, db_session):
    leg = make_legislation(title="Detail Bill")
    db_session.add(leg)
    db_session.flush()

    db_session.add(
        LegislationAction(
            legislation_id=leg.id,
            action_date=date(2025, 2, 1),
            description="Referred to committee",
            action_type="Referral",
            display_order=1,
        )
    )
    db_session.add(
        LegislationAction(
            legislation_id=leg.id,
            action_date=date(2025, 3, 1),
            description="Committee vote",
            action_type="Vote",
            display_order=2,
        )
    )
    db_session.commit()

    resp = integration_client.get(f"/api/legislation/{leg.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Detail Bill"
    assert len(data["actions"]) == 2
    assert data["actions"][0]["action_type"] == "Referral"
    assert data["actions"][1]["action_type"] == "Vote"


def test_get_legislation_actions_ordered_by_display_order(integration_client, db_session):
    leg = make_legislation()
    db_session.add(leg)
    db_session.flush()

    # Insert in reverse display order to confirm sorting
    db_session.add(
        LegislationAction(
            legislation_id=leg.id,
            action_date=date(2025, 1, 1),
            description="Second",
            action_type="Vote",
            display_order=2,
        )
    )
    db_session.add(
        LegislationAction(
            legislation_id=leg.id,
            action_date=date(2025, 1, 1),
            description="First",
            action_type="Referral",
            display_order=1,
        )
    )
    db_session.commit()

    resp = integration_client.get(f"/api/legislation/{leg.id}")
    actions = resp.json()["actions"]
    assert actions[0]["description"] == "First"
    assert actions[1]["description"] == "Second"


def test_get_legislation_not_found(integration_client):
    resp = integration_client.get("/api/legislation/99999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /api/legislation/recent
# ---------------------------------------------------------------------------


def test_get_recent_legislation_default_limit(integration_client, db_session):
    for i in range(15):
        db_session.add(
            make_legislation(
                bill_number=f"SB-{i:03}",
                title=f"Bill {i}",
                date_introduced=date(2025, 1, i + 1),
            )
        )
    db_session.commit()

    resp = integration_client.get("/api/legislation/recent")
    assert resp.status_code == 200
    assert len(resp.json()) == 10
    assert "actions" not in resp.json()[0]


def test_get_recent_legislation_custom_limit(integration_client, db_session):
    for i in range(5):
        db_session.add(make_legislation(bill_number=f"SB-{i:03}", title=f"Bill {i}"))
    db_session.commit()

    resp = integration_client.get("/api/legislation/recent?limit=3")
    assert len(resp.json()) == 3


def test_get_recent_legislation_filter_by_type(integration_client, db_session):
    db_session.add(make_legislation(type="Bill", title="A Bill"))
    db_session.add(make_legislation(type="Nomination", title="A Nomination", bill_number="SB-002"))
    db_session.commit()

    resp = integration_client.get("/api/legislation/recent?type=Nomination")
    items = resp.json()
    assert len(items) == 1
    assert items[0]["type"] == "Nomination"


def test_get_recent_legislation_ordered_most_recent_first(integration_client, db_session):
    db_session.add(make_legislation(title="Older", date_introduced=date(2025, 1, 1)))
    db_session.add(
        make_legislation(title="Newer", bill_number="SB-002", date_introduced=date(2025, 6, 1))
    )
    db_session.commit()

    resp = integration_client.get("/api/legislation/recent")
    items = resp.json()
    assert items[0]["title"] == "Newer"
    assert items[1]["title"] == "Older"
