from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .SenatorDTO import SenatorDTO


class DistrictDTO(BaseModel):
    id: int
    district_name: str
    description: Optional[str] = None
    senator: Optional[List[SenatorDTO]] = None

    model_config = ConfigDict(from_attributes=True)
