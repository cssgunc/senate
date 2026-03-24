"""Integration tests for GET /api/districts and GET /api/districts/lookup (TDD Section 4.5.2)."""


class TestListDistricts:
    def test_returns_200(self, client):
        assert client.get("/api/districts").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/districts").json()
        assert isinstance(data, list)

    def test_returns_all_districts(self, client):
        data = client.get("/api/districts").json()
        names = {d["district_name"] for d in data}
        assert "On-Campus" in names
        assert "Off-Campus" in names

    def test_district_fields_present(self, client):
        district = client.get("/api/districts").json()[0]
        for field in ("id", "district_name", "senator"):
            assert field in district, f"Field '{field}' missing from district"

    def test_nested_senators_is_list(self, client):
        data = client.get("/api/districts").json()
        for district in data:
            assert isinstance(district["senator"], list)

    def test_on_campus_has_active_senator(self, client):
        """Alice Smith is active and assigned to On-Campus district."""
        data = client.get("/api/districts").json()
        on_campus = next(d for d in data if d["district_name"] == "On-Campus")
        names = {s["first_name"] for s in on_campus["senator"]}
        assert "Alice" in names

    def test_inactive_senator_excluded_from_district(self, client):
        """Carol Lee is inactive — must not appear nested under On-Campus."""
        data = client.get("/api/districts").json()
        on_campus = next(d for d in data if d["district_name"] == "On-Campus")
        names = {s["first_name"] for s in on_campus["senator"]}
        assert "Carol" not in names

    def test_nested_senator_fields_present(self, client):
        data = client.get("/api/districts").json()
        on_campus = next(d for d in data if d["district_name"] == "On-Campus")
        senator = on_campus["senator"][0]
        for field in ("id", "first_name", "last_name", "email", "district_id", "committees"):
            assert field in senator, f"Field '{field}' missing from nested senator"


class TestDistrictLookup:
    def test_returns_200_with_match(self, client):
        assert client.get("/api/districts/lookup?query=on-campus").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/districts/lookup?query=on-campus").json()
        assert isinstance(data, list)

    def test_exact_match(self, client):
        data = client.get("/api/districts/lookup?query=on-campus").json()
        assert len(data) == 1
        assert data[0]["district_name"] == "On-Campus"

    def test_partial_match(self, client):
        """'campus' matches both on-campus and off-campus mappings."""
        data = client.get("/api/districts/lookup?query=campus").json()
        assert len(data) == 2

    def test_case_insensitive(self, client):
        upper = client.get("/api/districts/lookup?query=ON-CAMPUS").json()
        lower = client.get("/api/districts/lookup?query=on-campus").json()
        assert len(upper) == len(lower) == 1

    def test_no_match_returns_empty_list(self, client):
        data = client.get("/api/districts/lookup?query=zzznomatch").json()
        assert data == []

    def test_missing_query_returns_422(self, client):
        assert client.get("/api/districts/lookup").status_code == 422

    def test_lookup_result_includes_nested_senators(self, client):
        data = client.get("/api/districts/lookup?query=off-campus").json()
        assert len(data) == 1
        assert isinstance(data[0]["senator"], list)
        names = {s["first_name"] for s in data[0]["senator"]}
        assert "Bob" in names
