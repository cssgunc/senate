"""Tests for core entity models (Issue #3): Admin, Senator, District, Leadership, Sections.

Uses SQLAlchemy metadata inspection — no live database required.
"""

from app.models import (
    Admin,
    AdminSections,
    District,
    DistrictMapping,
    Leadership,
    Sections,
    Senator,
)

# --- Helper ---


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


# --- Admin ---


class TestAdminModel:
    def test_table_name(self):
        assert Admin.__tablename__ == "admin"

    def test_columns_exist(self):
        cols = get_columns(Admin)
        expected = {
            "id",
            "email",
            "first_name",
            "last_name",
            "pid",
            "role",
            "created_at",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_pid_is_char_9(self):
        cols = get_columns(Admin)
        assert cols["pid"].type.length == 9

    def test_pid_check_constraint(self):
        # Verify via __table_args__ (table.constraints may be modified by test conftest for SQLite)
        from sqlalchemy import CheckConstraint

        check_constraints = [c for c in Admin.__table_args__ if isinstance(c, CheckConstraint)]
        assert len(check_constraints) == 1
        assert check_constraints[0].name == "ck_admin_pid_format"

    def test_email_is_unique(self):
        cols = get_columns(Admin)
        assert cols["email"].unique is True

    def test_pid_is_unique(self):
        cols = get_columns(Admin)
        assert cols["pid"].unique is True

    def test_updated_at_has_onupdate(self):
        cols = get_columns(Admin)
        assert cols["updated_at"].onupdate is not None


# --- District ---


class TestDistrictModel:
    def test_table_name(self):
        assert District.__tablename__ == "district"

    def test_columns_exist(self):
        cols = get_columns(District)
        expected = {"id", "district_name", "description"}
        assert expected == set(cols.keys())

    def test_description_nullable(self):
        cols = get_columns(District)
        assert cols["description"].nullable is True


# --- DistrictMapping ---


class TestDistrictMappingModel:
    def test_table_name(self):
        assert DistrictMapping.__tablename__ == "district_mapping"

    def test_columns_exist(self):
        cols = get_columns(DistrictMapping)
        expected = {"id", "district_id", "mapping_value"}
        assert expected == set(cols.keys())

    def test_fk_to_district(self):
        assert "district" in get_fk_target_tables(DistrictMapping)


# --- Senator ---


class TestSenatorModel:
    def test_table_name(self):
        assert Senator.__tablename__ == "senator"

    def test_columns_exist(self):
        cols = get_columns(Senator)
        expected = {
            "id",
            "first_name",
            "last_name",
            "email",
            "headshot_url",
            "district",
            "is_active",
            "session_number",
            "created_at",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_headshot_url_nullable(self):
        cols = get_columns(Senator)
        assert cols["headshot_url"].nullable is True

    def test_fk_to_district(self):
        assert "district" in get_fk_target_tables(Senator)

    def test_updated_at_has_onupdate(self):
        cols = get_columns(Senator)
        assert cols["updated_at"].onupdate is not None


# --- Leadership ---


class TestLeadershipModel:
    def test_table_name(self):
        assert Leadership.__tablename__ == "leadership"

    def test_columns_exist(self):
        cols = get_columns(Leadership)
        expected = {
            "id",
            "senator_id",
            "title",
            "first_name",
            "last_name",
            "email",
            "headshot_url",
            "is_active",
            "session_number",
            "created_at",
            "updated_at",
        }
        assert expected == set(cols.keys())

    def test_senator_id_nullable(self):
        cols = get_columns(Leadership)
        assert cols["senator_id"].nullable is True

    def test_fk_to_senator(self):
        assert "senator" in get_fk_target_tables(Leadership)

    def test_updated_at_has_onupdate(self):
        cols = get_columns(Leadership)
        assert cols["updated_at"].onupdate is not None


# --- Sections ---


class TestSectionsModel:
    def test_table_name(self):
        assert Sections.__tablename__ == "sections"

    def test_columns_exist(self):
        cols = get_columns(Sections)
        expected = {"id", "name"}
        assert expected == set(cols.keys())


# --- AdminSections ---


class TestAdminSectionsModel:
    def test_table_name(self):
        assert AdminSections.__tablename__ == "admin_sections"

    def test_columns_exist(self):
        cols = get_columns(AdminSections)
        expected = {"id", "section_id", "admin_id"}
        assert expected == set(cols.keys())

    def test_fk_to_sections(self):
        assert "sections" in get_fk_target_tables(AdminSections)

    def test_fk_to_admin(self):
        assert "admin" in get_fk_target_tables(AdminSections)


# --- __init__.py exports ---


def test_all_core_models_exported():
    from app import models

    expected = {
        "Admin",
        "District",
        "DistrictMapping",
        "Senator",
        "Leadership",
        "Sections",
        "AdminSections",
    }
    assert expected.issubset(set(models.__all__))
