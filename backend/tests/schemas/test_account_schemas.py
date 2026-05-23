"""Tests for account input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.account import AccountDTO, CreateAccountDTO, UpdateAccountDTO


class TestCreateAccountDTO:
    def test_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            onyen="JaneDoe",
            password="TestPassword123!",
            first_name="Jane",
            last_name="Doe",
            role="admin",
        )
        assert dto.onyen == "janedoe"
        assert dto.role == "admin"

    def test_invalid_onyen_too_short(self):
        with pytest.raises(ValidationError, match="Onyen must be 2-64 characters"):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="x",
                password="TestPassword123!",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_onyen_with_spaces(self):
        with pytest.raises(ValidationError, match="Onyen must be 2-64 characters"):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="jane doe",
                password="TestPassword123!",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_password_too_short(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="janedoe",
                password="short",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="not-an-email",
                onyen="janedoe",
                password="TestPassword123!",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_role(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="janedoe",
                password="TestPassword123!",
                first_name="Jane",
                last_name="Doe",
                role="superuser",
            )

    def test_staff_role_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            onyen="janedoe",
            password="TestPassword123!",
            first_name="Jane",
            last_name="Doe",
            role="staff",
        )
        assert dto.role == "staff"


class TestUpdateAccountDTO:
    def test_password_is_optional(self):
        dto = UpdateAccountDTO(first_name="Jane")
        assert dto.password is None


class TestAccountDTO:
    def test_from_attributes(self):
        class FakeAdmin:
            id = 1
            email = "user@unc.edu"
            onyen = "janedoe"
            first_name = "Jane"
            last_name = "Doe"
            role = "admin"

        dto = AccountDTO.model_validate(FakeAdmin())
        assert dto.id == 1
        assert dto.onyen == "janedoe"
        assert dto.role == "admin"
