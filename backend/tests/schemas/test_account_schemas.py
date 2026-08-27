"""Tests for account input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.account import AccountDTO, CreateAccountDTO


class TestCreateAccountDTO:
    def test_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            onyen="JaneDoe",
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
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_onyen_with_spaces(self):
        with pytest.raises(ValidationError, match="Onyen must be 2-64 characters"):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="jane doe",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="not-an-email",
                onyen="janedoe",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_role(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="user@unc.edu",
                onyen="janedoe",
                first_name="Jane",
                last_name="Doe",
                role="superuser",
            )

    def test_staff_role_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            onyen="janedoe",
            first_name="Jane",
            last_name="Doe",
            role="staff",
        )
        assert dto.role == "staff"


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
