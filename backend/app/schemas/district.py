"""District schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict

from app.schemas.senator import SenatorDTO


class DistrictDTO(BaseModel):
    id: int
    district_name: str
    description: str | None
    senator: list[SenatorDTO] | None

    model_config = ConfigDict(from_attributes=True)


class AdminDistrictDTO(BaseModel):
    id: int
    district_name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class DistrictLookupDTO(BaseModel):
    query: str


class CreateDistrictDTO(BaseModel):
    district_name: str
    description: str | None = None


class UpdateDistrictDTO(BaseModel):
    district_name: str | None = None
    description: str | None = None
