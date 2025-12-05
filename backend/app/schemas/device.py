"""Pydantic schemas for Device."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DeviceStatus(str, Enum):
    """Valid status values for devices."""

    ACTIVE = "active"
    PLANNED = "planned"
    STAGED = "staged"
    FAILED = "failed"
    OFFLINE = "offline"
    DECOMMISSIONING = "decommissioning"


class DeviceBase(BaseModel):
    """Base schema for Device."""

    name: str = Field(..., min_length=1, max_length=64)
    device_type_id: int
    role_id: int
    site_id: int
    status: DeviceStatus = Field(default=DeviceStatus.ACTIVE)
    serial: str | None = Field(default=None, max_length=50)
    asset_tag: str | None = Field(default=None, max_length=50)
    rack_id: int | None = None
    rack_position: int | None = Field(default=None, ge=1)
    tenant_id: int | None = None
    description: str | None = Field(default=None, max_length=200)
    tags: list[str] = Field(default_factory=list)


class DeviceCreate(DeviceBase):
    """Schema for creating a new device."""

    pass


class DeviceUpdate(BaseModel):
    """Schema for updating an existing device."""

    name: str | None = None
    status: DeviceStatus | None = None
    serial: str | None = None
    asset_tag: str | None = None
    rack_id: int | None = None
    rack_position: int | None = None
    tenant_id: int | None = None
    description: str | None = None
    tags: list[str] | None = None


class DeviceResponse(BaseModel):
    """Schema for device response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    device_type_id: int | None = None
    device_type_name: str | None = None
    role_id: int | None = None
    role_name: str | None = None
    site_id: int | None = None
    site_name: str | None = None
    status: str = "active"
    serial: str = ""
    description: str = ""
    tags: list[str] = []
    created: datetime
    last_updated: datetime
