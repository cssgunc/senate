"""Tests for account input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.account import AccountDTO, CreateAccountDTO


class TestCreateAccountDTO:
    def test_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            pid="123456789",
            first_name="Jane",
            last_name="Doe",
            role="admin",
        )
        assert dto.pid == "123456789"
        assert dto.role == "admin"

    def test_invalid_pid_too_short(self):
        with pytest.raises(ValidationError, match="PID must be exactly 9 digits"):
            CreateAccountDTO(
                email="user@unc.edu",
                pid="12345",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_pid_too_long(self):
        with pytest.raises(ValidationError, match="PID must be exactly 9 digits"):
            CreateAccountDTO(
                email="user@unc.edu",
                pid="1234567890",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_pid_non_digits(self):
        with pytest.raises(ValidationError, match="PID must be exactly 9 digits"):
            CreateAccountDTO(
                email="user@unc.edu",
                pid="12345678a",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="not-an-email",
                pid="123456789",
                first_name="Jane",
                last_name="Doe",
                role="admin",
            )

    def test_invalid_role(self):
        with pytest.raises(ValidationError):
            CreateAccountDTO(
                email="user@unc.edu",
                pid="123456789",
                first_name="Jane",
                last_name="Doe",
                role="superuser",
            )

    def test_staff_role_valid(self):
        dto = CreateAccountDTO(
            email="user@unc.edu",
            pid="000000000",
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
            pid = "123456789"
            first_name = "Jane"
            last_name = "Doe"
            role = "admin"

        dto = AccountDTO.model_validate(FakeAdmin())
        assert dto.id == 1
        assert dto.role == "admin"
