import app.enums as enums
import typing

from typing_extensions import Self
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator, model_validator
from croniter import croniter

class Base(SQLModel):
    pass

class Credential(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    data: typing.Optional[str] = Field(default="{}")
    username: str | None = Field()
    password: str | None = Field()
    deleted: typing.Optional[bool] = False
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class WorkItem(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data: str
    reference: str | None = Field(default="")
    locked: bool
    status: enums.WorkItemStatus
    message: str = ""
    workqueue_id: int = Field(foreign_key="workqueue.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

class Workqueue(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1)
    description: typing.Optional[str]
    enabled: bool = Field(default=True)

    deleted: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class Process(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    description: typing.Optional[str] = ""

    requirements: typing.Optional[str] = ""

    target_type: enums.TargetTypeEnum | None = None
    target_source: typing.Optional[str] = ""

    target_credentials_id: typing.Optional[int] | None = Field(
        default=None, foreign_key="credential.id"
    )
    credentials_id: typing.Optional[int] = Field(
        default=None, foreign_key="credential.id"
    )

    workqueue_id: int | None = Field(default=None, foreign_key="workqueue.id")
    workqueue: typing.Optional[Workqueue] = Relationship()

    deleted: typing.Optional[bool] = False

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    triggers: typing.List["Trigger"] = Relationship(back_populates="process")


class Trigger(Base, table=True):
    id: int | None = Field(default=None, primary_key=True)

    type: enums.TriggerType

    # Used for the cron trigger type
    cron: str

    # Used for the date trigger type
    date: typing.Optional[datetime]

    # Used for the workqueue trigger type
    workqueue_id: int | None = Field(default=None, foreign_key="workqueue.id")
    workqueue_resource_limit: int = 0
    workqueue_scale_up_threshold: int = 0

    deleted: typing.Optional[bool] = False
    enabled: typing.Optional[bool] = False

    last_triggered: typing.Optional[datetime] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    process_id: int = Field(foreign_key="process.id")
    process: Process = Relationship(back_populates="triggers")

    @field_validator("cron")
    def validate_cron(cls, v):
        # If type is not cron, we don't need to validate the cron string and return empty string
        if cls.type != enums.TriggerType.CRON:
            return ""

        if not croniter.is_valid(v):
            raise ValueError("Invalid cron string")
        return v

    @model_validator(mode="after")
    def validate_trigger_combinations(self) -> Self:
        if self.type == enums.TriggerType.CRON:
            if self.date is not None:
                raise ValueError("A cron trigger cannot have a date")
            if self.workqueue_id is not None:
                raise ValueError("A cron trigger cannot have a workqueue")

        if self.type == enums.TriggerType.DATE:
            # Cron can be none or empty string
            if self.cron is not None and self.cron != "":
                raise ValueError("A date trigger cannot have a cron")

            if self.workqueue_id is not None:
                raise ValueError("A date trigger cannot have a workqueue")

        if self.type == enums.TriggerType.WORKQUEUE:
            # Cron can be none or empty string
            if self.cron is not None and self.cron != "":
                raise ValueError("A workqueue trigger cannot have a cron")
            if self.date is not None:
                raise ValueError("A workqueue trigger cannot have a date")

        return self


class Resource(Base, table=True):
    id: int = Field(default=None, primary_key=True)

    name: str
    fqdn: str
    capabilities: str

    available: bool = Field()

    last_seen: typing.Optional[datetime] = Field()

    deleted: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class Session(Base, table=True):
    id: int = Field(default=None, primary_key=True)

    process_id: int = Field(foreign_key="process.id")
    process: typing.Optional[Process] = Relationship()

    resource_id: typing.Optional[int] = Field(foreign_key="resource.id")
    resource: typing.Optional[Resource] = Relationship()

    dispatched_at: typing.Optional[datetime] = Field()
    status: enums.SessionStatus = Field()

    stop_requested: bool = Field(default=False)

    deleted: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class SystemLog(Base, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    message: str
    level: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class SessionLog(Base, table=True):
    id: typing.Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="session.id")
    session: Session = Relationship()

    workitem_id: typing.Optional[int] = Field(foreign_key="workitem.id")
    workitem: typing.Optional[WorkItem] = Relationship()
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now())


class AccessToken(Base, table=True):
    id: int = Field(default=None, primary_key=True)
    identifier: str = Field(index=True, unique=True)
    access_token: str = Field(index=True, unique=True)

    expires_at: datetime = None

    deleted: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())