"""Pydantic schemas for VLAN."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class VlanStatus(str, Enum):
    """Valid status values for VLANs."""

    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"


class VlanBase(BaseModel):
    """Base schema for VLAN."""

    name: str = Field(..., min_length=1, max_length=64)
    vid: int = Field(..., ge=1, le=4094, description="VLAN ID (1-4094)")
    status: VlanStatus = Field(default=VlanStatus.ACTIVE)
    description: str | None = Field(default=None, max_length=200)
    site_id: int | None = None
    tenant_id: int | None = None
    group_id: int | None = None
    tags: list[str] = Field(default_factory=list)


class VlanCreate(VlanBase):
    """Schema for creating a new VLAN."""

    pass


class VlanUpdate(BaseModel):
    """Schema for updating an existing VLAN."""

    name: str | None = None
    status: VlanStatus | None = None
    description: str | None = None
    site_id: int | None = None
    tenant_id: int | None = None
    group_id: int | None = None
    tags: list[str] | None = None


class VlanResponse(VlanBase):
    """Schema for VLAN response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    last_updated: datetime
