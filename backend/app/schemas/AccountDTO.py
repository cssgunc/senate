from typing import Literal

from pydantic import BaseModel, ConfigDict


class AccountDTO(BaseModel):
    id: int
    email: str
    pid: str
    first_name: str
    last_name: str
    role: Literal["admin", "staff"]

    model_config = ConfigDict(from_attributes=True)

