"""VLAN Group schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.slug import generate_slug


class VlanGroupBase(BaseModel):
    """Base schema for VLAN Group."""

    name: str = Field(..., min_length=1, max_length=100, description="VLAN Group name")
    slug: str | None = Field(None, max_length=100, description="URL-friendly slug")
    description: str = Field(default="", max_length=500, description="VLAN Group description")
    vid_ranges: str | None = Field(None, description="VLAN ID ranges (e.g., '100-199,300-399')")
    tags: list[str] = Field(default_factory=list, description="Associated tags")


class VlanGroupCreate(VlanGroupBase):
    """Schema for creating a VLAN group."""

    @field_validator("slug", mode="before")
    @classmethod
    def auto_generate_slug(cls, v: str | None, info) -> str:
        """Auto-generate slug from name if not provided."""
        if v:
            return v
        name = info.data.get("name", "")
        return generate_slug(name) if name else ""


class VlanGroupUpdate(BaseModel):
    """Schema for updating a VLAN group."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    vid_ranges: str | None = None
    tags: list[str] | None = None


class VlanGroupResponse(VlanGroupBase):
    """Schema for VLAN group response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    last_updated: datetime
