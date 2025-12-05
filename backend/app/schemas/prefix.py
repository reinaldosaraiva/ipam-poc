"""Pydantic schemas for IP Prefix (IPAM)."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator
import ipaddress


class PrefixStatus(str, Enum):
    """Valid status values for IP prefixes."""

    ACTIVE = "active"
    RESERVED = "reserved"
    DEPRECATED = "deprecated"
    CONTAINER = "container"


class PrefixBase(BaseModel):
    """Base schema for IP Prefix."""

    prefix: str = Field(..., description="CIDR notation (e.g., 10.0.0.0/24)")
    status: PrefixStatus = Field(default=PrefixStatus.ACTIVE)
    description: str | None = Field(default=None, max_length=200)
    site_id: int | None = None
    tenant_id: int | None = None
    vlan_id: int | None = None
    role_id: int | None = None
    is_pool: bool = Field(default=False)
    tags: list[str] = Field(default_factory=list)

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Validate that prefix is a valid CIDR notation."""
        try:
            ipaddress.ip_network(v, strict=False)
        except ValueError as e:
            raise ValueError(f"Invalid CIDR notation: {e}") from e
        return v


class PrefixCreate(PrefixBase):
    """Schema for creating a new prefix."""

    pass


class PrefixUpdate(BaseModel):
    """Schema for updating an existing prefix."""

    status: PrefixStatus | None = None
    description: str | None = None
    site_id: int | None = None
    tenant_id: int | None = None
    vlan_id: int | None = None
    role_id: int | None = None
    is_pool: bool | None = None
    tags: list[str] | None = None


class NestedSite(BaseModel):
    """Nested site representation."""

    id: int
    name: str


class NestedTenant(BaseModel):
    """Nested tenant representation."""

    id: int
    name: str


class PrefixResponse(PrefixBase):
    """Schema for prefix response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    site: NestedSite | None = None
    tenant: NestedTenant | None = None
    created: datetime
    last_updated: datetime
