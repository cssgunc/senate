"""Pydantic schemas"""

from .account import AccountDTO, CreateAccountDTO
from .budget import BudgetDataDTO, CreateBudgetDataDTO
from .calendar_event import CalendarEventDTO, CreateCalendarEventDTO
from .carousel import CarouselSlideDTO, CreateCarouselSlideDTO
from .committee import (
    AssignCommitteeMemberDTO,
    CommitteeDTO,
    CreateCommitteeDTO,
)
from .district import DistrictDTO, DistrictLookupDTO
from .finance import (
    CreateFinanceHearingDateDTO,
    FinanceHearingConfigDTO,
    FinanceHearingDateDTO,
    UpdateFinanceHearingConfigDTO,
)
from .leadership import LeadershipDTO
from .legislation import (
    CreateLegislationActionDTO,
    CreateLegislationDTO,
    LegislationActionDTO,
    LegislationDetailDTO,
    LegislationDTO,
    LegislationListDTO,
)
from .news import CreateNewsDTO, NewsDTO, UpdateNewsDTO
from .senator import (
    CommitteeAssignmentDTO,
    CreateSenatorDTO,
    SenatorDTO,
    UpdateSenatorDTO,
)
from .staff import CreateStaffDTO, StaffDTO
from .static_page import StaticPageDTO, UpdateStaticPageDTO

__all__ = [
    # Account
    "AccountDTO",
    "CreateAccountDTO",
    # Budget
    "BudgetDataDTO",
    "CreateBudgetDataDTO",
    # Calendar Event
    "CalendarEventDTO",
    "CreateCalendarEventDTO",
    # Carousel
    "CarouselSlideDTO",
    "CreateCarouselSlideDTO",
    # Committee
    "AssignCommitteeMemberDTO",
    "CommitteeDTO",
    "CreateCommitteeDTO",
    # District
    "DistrictDTO",
    "DistrictLookupDTO",
    # Finance
    "CreateFinanceHearingDateDTO",
    "FinanceHearingConfigDTO",
    "FinanceHearingDateDTO",
    "UpdateFinanceHearingConfigDTO",
    # Leadership
    "LeadershipDTO",
    # Legislation
    "CreateLegislationActionDTO",
    "CreateLegislationDTO",
    "LegislationActionDTO",
    "LegislationDetailDTO",
    "LegislationDTO",
    "LegislationListDTO",
    # News
    "CreateNewsDTO",
    "NewsDTO",
    "UpdateNewsDTO",
    # Senator
    "CommitteeAssignmentDTO",
    "CreateSenatorDTO",
    "SenatorDTO",
    "UpdateSenatorDTO",
    # Staff
    "CreateStaffDTO",
    "StaffDTO",
    # Static Page
    "StaticPageDTO",
    "UpdateStaticPageDTO",
]
