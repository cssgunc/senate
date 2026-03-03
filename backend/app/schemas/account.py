"""Account schemas — input and output DTOs."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class AccountDTO(BaseModel):
    id: int
    email: EmailStr
    pid: str
    first_name: str
    last_name: str
    role: Literal["admin", "staff"]

    model_config = ConfigDict(from_attributes=True)


class CreateAccountDTO(BaseModel):
    email: EmailStr
    pid: str
    first_name: str
    last_name: str
    role: Literal["admin", "staff"]

    @field_validator("pid")
    @classmethod
    def pid_must_be_nine_digits(cls, v: str) -> str:
        if not re.fullmatch(r"\d{9}", v):
            raise ValueError("PID must be exactly 9 digits")
        return v
