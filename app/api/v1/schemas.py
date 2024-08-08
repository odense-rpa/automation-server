from typing import Optional
from typing import Generic, TypeVar, List
from pydantic.generics import GenericModel

from typing_extensions import Self
from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from croniter import croniter
from app import enums


class WorkqueueUpdate(BaseModel):
    name: str = Field(min_length=1)
    description: str
    enabled: bool


class WorkqueueCreate(BaseModel):
    name: str = Field(min_length=1)
    description: str
    enabled: bool

class WorkqueueInformation(BaseModel):
    id: int
    name: str = Field(min_length=1)
    description: str
    enabled: bool
    new: int
    in_progress: int
    completed: int
    failed: int
    pending_user_action: int
    



class WorkItemCreate(BaseModel):
    data: str
    reference: Optional[str] = ""


class WorkItemUpdate(BaseModel):
    data: str
    reference: Optional[str] = ""


class WorkItemStatusUpdate(BaseModel):
    status: enums.WorkItemStatus


class ProcessCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    requirements: Optional[str] = ""
    target_type: enums.TargetTypeEnum
    target_source: Optional[str] = ""
    target_credentials_id: Optional[int]
    credentials_id: Optional[int]
    workqueue_id: int
    requirements: Optional[str] = ""


class ProcessUpdate(ProcessCreate):
    pass


class TriggerCreate(BaseModel):
    type: enums.TriggerType
    cron: Optional[str] = ""

    date: Optional[datetime] = None

    workqueue_id: int | None = None
    workqueue_resource_limit: int = 0
    workqueue_scale_up_threshold: int = 0

    enabled: bool = False

    @model_validator(mode='after')
    def validate_trigger_type(self) -> Self:

        if self.type == enums.TriggerType.CRON and (self.cron is None or self.cron == "" or not croniter.is_valid(self.cron)):
            raise ValueError("Cron must be set for cron triggers")

        if self.type == enums.TriggerType.DATE and self.date is None:
            raise ValueError("Date must be set for date triggers")

        if self.type == enums.TriggerType.WORKQUEUE and self.workqueue_id is None:
            raise ValueError("Workqueue must be set for workqueue triggers")

        return self

class TriggerUpdate(TriggerCreate):
    pass



class CredentialCreate(BaseModel):
    name: str
    username: Optional[str] = ""
    password: Optional[str] = ""


class CredentialUpdate(CredentialCreate):
    pass


class ResourceCreate(BaseModel):
    name: str
    fqdn: str
    capabilities: str


class ResourceUpdate(ResourceCreate):
    pass


class SessionCreate(BaseModel):
    process_id: int


class SessionStatusUpdate(BaseModel):
    status: Optional[enums.SessionStatus] = None

class SessionResourceUpdate(BaseModel):
    resource_id: Optional[int] = None

class SessionLogCreate(BaseModel):
    workitem_id: Optional[int] = None
    message: str


# Schemas for the API
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number, starting from 1")
    size: int = Field(50, ge=1, le=200, description="Number of items per page")

class SearchParams(BaseModel):
    search: Optional[str] = Field(None, description="Search term")

class PaginatedSearchParams(BaseModel):
    pagination: PaginationParams
    search: Optional[str]


T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    page: int
    size: int
    total_items: int
    total_pages: int
    items: List[T]