import json

from typing import Optional, Dict, Any
from typing import Generic, TypeVar, List
from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from cronsim import CronSim, CronSimError
from app import enums

class AccessTokenCreate(BaseModel):
    identifier: str

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
    data: Dict = {}
    reference: Optional[str] = ""

class WorkItemUpdate(BaseModel):
    data: Optional[Dict] = None
    reference: Optional[str] = None

class WorkItemStatusUpdate(BaseModel):
    status: enums.WorkItemStatus

class WorkItemRead(BaseModel):
    id: int
    data: Dict
    reference: str | None
    locked: bool
    status: enums.WorkItemStatus
    message: str
    workqueue_id: int
    started_at: datetime | None
    work_duration_seconds: int | None
    created_at: datetime
    updated_at: datetime

class ProcessCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    requirements: Optional[str] = ""
    target_type: enums.TargetTypeEnum
    target_source: Optional[str] = ""
    target_credentials_id: Optional[int] = None
    credentials_id: Optional[int] = None
    workqueue_id: Optional[int] = None
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

    parameters: Optional[str] = ""

    enabled: bool = False

    @model_validator(mode='after')
    def validate_trigger_type(self) -> Self:

        if self.type == enums.TriggerType.CRON:
            if self.cron is None or self.cron == "":
                raise ValueError("Cron must be set for cron triggers")
            try:
                # We use a dummy datetime just for validation
                CronSim(self.cron, datetime.now())
            except CronSimError:
                raise ValueError("Invalid cron expression")

        if self.type == enums.TriggerType.DATE and self.date is None:
            raise ValueError("Date must be set for date triggers")

        if self.type == enums.TriggerType.WORKQUEUE and self.workqueue_id is None:
            raise ValueError("Workqueue must be set for workqueue triggers")

        return self

class TriggerUpdate(TriggerCreate):
    pass

class CredentialCreate(BaseModel):
    name: str
    data: Optional[Dict] = None
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
    parameters: Optional[str] = None

class SessionStatusUpdate(BaseModel):
    status: Optional[enums.SessionStatus] = None

class SessionResourceUpdate(BaseModel):
    resource_id: Optional[int] = None

class SessionLogCreate(BaseModel):
    # Foreign key relationships (both nullable)
    session_id: Optional[int] = None
    workitem_id: Optional[int] = None
    
    # Core logging fields
    message: str
    level: str = Field(default="INFO")
    logger_name: str = Field(default="")
    
    # Source location fields (from Python LogRecord)
    module: Optional[str] = None
    function_name: Optional[str] = None
    line_number: Optional[int] = None
    
    # Exception fields
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    traceback: Optional[str] = None
    
    # Structured data for audit trail (HTTP calls, UI automation, etc.)
    structured_data: Optional[Dict[str, Any]] = None
    
    # Event timestamp (when the log event actually occurred)
    event_timestamp: datetime
    
    class Config:
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "session_id": 123,
                "workitem_id": 456,
                "message": "API call completed successfully",
                "level": "INFO",
                "logger_name": "myapp.api",
                "module": "payment_processor.py",
                "function_name": "process_payment",
                "line_number": 45,
                "structured_data": {
                    "http": {
                        "method": "POST",
                        "url": "https://api.example.com/payment",
                        "response_status": 200,
                        "duration_ms": 1250
                    }
                },
                "event_timestamp": "2025-07-23T10:30:00Z"
            }
        }

class AccessTokenRead(BaseModel):
    id: int = Field(default=None, primary_key=True)
    identifier: str = Field(index=True, unique=True)
    expires_at: datetime = None
    deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now())

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

class PaginatedResponse(BaseModel, Generic[T]):
    page: int
    size: int
    total_items: int
    total_pages: int
    items: List[T]

class WorkqueueClear(BaseModel):
    workitem_status: Optional[enums.WorkItemStatus] = None
    days_older_than: Optional[int] = None

class UpcomingExecutionRead(BaseModel):
    trigger_id: int = Field(description="Unique identifier for the trigger")
    process_id: int = Field(description="Unique identifier for the associated process")
    process_name: str = Field(description="Name of the process")
    process_description: str = Field(description="Description of the process")
    next_execution: str = Field(description="Next execution time in ISO format")
    trigger_type: enums.TriggerType = Field(description="Type of trigger (cron, date, workqueue)")
    parameters: Optional[str] = Field(None, description="Optional parameters for the trigger")
    cron: Optional[str] = Field(None, description="Cron expression for cron triggers")
    date: Optional[str] = Field(None, description="Target date in ISO format for date triggers")