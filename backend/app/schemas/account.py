"""Account schemas — input and output DTOs."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

ONYEN_PATTERN = re.compile(r"^[A-Za-z0-9._-]{2,64}$")
MIN_PASSWORD_LENGTH = 12


def normalize_onyen(value: str) -> str:
    return value.strip().lower()


def validate_onyen(value: str) -> str:
    normalized = normalize_onyen(value)
    if not ONYEN_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Onyen must be 2-64 characters and may only contain letters, numbers, dots, underscores, or hyphens"
        )
    return normalized


class AccountDTO(BaseModel):
    id: int
    email: EmailStr
    onyen: str
    first_name: str
    last_name: str
    role: Literal["admin", "staff"]

    model_config = ConfigDict(from_attributes=True)


class CreateAccountDTO(BaseModel):
    email: EmailStr
    onyen: str
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)
    first_name: str
    last_name: str
    role: Literal["admin", "staff"]

    @field_validator("onyen")
    @classmethod
    def onyen_must_be_valid(cls, v: str) -> str:
        return validate_onyen(v)


class UpdateAccountDTO(BaseModel):
    email: EmailStr | None = None
    onyen: str | None = None
    password: str | None = Field(default=None, min_length=MIN_PASSWORD_LENGTH, max_length=128)
    first_name: str | None = None
    last_name: str | None = None
    role: Literal["admin", "staff"] | None = None

    @field_validator("onyen")
    @classmethod
    def onyen_must_be_valid(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return validate_onyen(v)
