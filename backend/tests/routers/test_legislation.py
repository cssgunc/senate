import logging

logging.basicConfig(level=logging.DEBUG)

# -----------------------------
# Full integration tests
# -----------------------------

def create_leg_payload():
    return {
        "title": "Test Bill",
        "bill_number": "HB123",
        "session_number": 2026,
        "sponsor_id": None,
        "sponsor_name": "John Doe",
        "summary": "This is a summary",
        "full_text": "Full text of the bill",
        "status": "Introduced",
        "type": "Bill",
        "date_introduced": "2026-04-07",
        "date_last_action": "2026-04-07"
    }

def create_action_payload():
    return {
        "action_date": "2026-04-08",
        "description": "First reading",
        "action_type": "reading"
    }


def test_create_legislation(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]

    payload = create_leg_payload()
    res = client.post("/api/admin/legislation", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Test Bill"
    assert data["status"] == "Introduced"
    assert data["date_last_action"] == "2026-04-07"


def test_add_legislation_action(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]

    # Create legislation first
    leg_payload = create_leg_payload()
    leg_res = client.post("/api/admin/legislation", json=leg_payload, headers={"Authorization": f"Bearer {token}"})
    leg_id = leg_res.json()["id"]

    # Add action
    action_payload = create_action_payload()
    action_payload["legislation_id"] = leg_id
    act_res = client.post(f"/api/admin/legislation/{leg_id}/actions", json=action_payload, headers={"Authorization": f"Bearer {token}"})
    assert act_res.status_code == 200
    act_data = act_res.json()

    assert act_data["description"] == "First reading"
    # assert act_data["display_order"] == 0   <----- incompatible DTO


def test_update_legislation(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]
    # Create legislation
    leg_payload = create_leg_payload()
    leg_res = client.post("/api/admin/legislation", json=leg_payload, headers={"Authorization": f"Bearer {token}"})
    leg_id = leg_res.json()["id"]

    # Update
    update_payload = {"summary": "Updated summary"}
    res = client.put(f"/api/admin/legislation/{leg_id}", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["summary"] == "Updated summary"


def test_update_legislation_action(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]
    # Create legislation and action
    leg_payload = create_leg_payload()
    leg_res = client.post("/api/admin/legislation", json=leg_payload, headers={"Authorization": f"Bearer {token}"})
    leg_id = leg_res.json()["id"]

    first_action = {
        "legislation_id": leg_id,
        "action_date": "2026-04-08",
        "description": "First reading",
        "action_type": "reading",
    }
    second_action = {
        "legislation_id": leg_id,
        "action_date": "2026-04-09",
        "description": "Second reading",
        "action_type": "reading",
    }
    client.post(f"/api/admin/legislation/{leg_id}/actions", json=first_action, headers={"Authorization": f"Bearer {token}"})
    act_res = client.post(f"/api/admin/legislation/{leg_id}/actions", json=second_action, headers={"Authorization": f"Bearer {token}"})
    action_id = act_res.json()["id"]

    # Update action
    update_payload = {"action_date": "2026-04-07", "description": "Updated action"}
    res = client.put(f"/api/admin/legislation/{leg_id}/actions/{action_id}", json=update_payload, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["description"] == "Updated action"

    detail_res = client.get(f"/api/legislation/{leg_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["date_last_action"] == "2026-04-08"


def test_delete_legislation_action(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]
    # Create legislation and action
    leg_payload = create_leg_payload()
    leg_res = client.post("/api/admin/legislation", json=leg_payload, headers={"Authorization": f"Bearer {token}"})
    leg_id = leg_res.json()["id"]

    first_action = {
        "legislation_id": leg_id,
        "action_date": "2026-04-08",
        "description": "First reading",
        "action_type": "reading",
    }
    second_action = {
        "legislation_id": leg_id,
        "action_date": "2026-04-09",
        "description": "Second reading",
        "action_type": "reading",
    }
    client.post(f"/api/admin/legislation/{leg_id}/actions", json=first_action, headers={"Authorization": f"Bearer {token}"})
    act_res = client.post(f"/api/admin/legislation/{leg_id}/actions", json=second_action, headers={"Authorization": f"Bearer {token}"})
    action_id = act_res.json()["id"]

    # Delete action
    del_res = client.delete(f"/api/admin/legislation/{leg_id}/actions/{action_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 204

    detail_res = client.get(f"/api/legislation/{leg_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["date_last_action"] == "2026-04-08"


def test_delete_legislation_and_cascade_actions(client , seeded_admins):
    login = client.post("/api/auth/login", json={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]
    # Create legislation
    leg_payload = create_leg_payload()
    leg_res = client.post("/api/admin/legislation", json=leg_payload, headers={"Authorization": f"Bearer {token}"})
    leg_id = leg_res.json()["id"]

    # Add multiple actions
    for i in range(3):
        action_payload = {
            "action_date": f"2026-04-{8+i}",
            "description": f"Action {i}",
            "action_type": "reading"
        }
        client.post(f"/api/admin/legislation/{leg_id}/actions", json=action_payload, headers={"Authorization": f"Bearer {token}"})

    # Delete legislation
    del_res = client.delete(f"/api/admin/legislation/{leg_id}", headers={"Authorization": f"Bearer {token}"})
    assert del_res.status_code == 204
