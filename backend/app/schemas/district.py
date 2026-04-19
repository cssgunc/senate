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


class DistrictMappingDTO(BaseModel):
    id: int
    district_id: int
    mapping_value: str

    model_config = ConfigDict(from_attributes=True)


class CreateDistrictMappingDTO(BaseModel):
    mapping_value: str


class AdminDistrictWithMappingsDTO(BaseModel):
    id: int
    district_name: str
    description: str | None
    mappings: list[DistrictMappingDTO] = []

    model_config = ConfigDict(from_attributes=True)
