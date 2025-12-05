"""Site schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.slug import generate_slug


class SiteBase(BaseModel):
    """Base schema for Site."""

    name: str = Field(..., min_length=1, max_length=100, description="Site name")
    slug: str | None = Field(None, max_length=100, description="URL-friendly slug")
    status: str = Field(
        default="active",
        description="Operational status",
    )
    description: str = Field(default="", max_length=500, description="Site description")
    tenant_id: int | None = Field(None, description="Associated tenant ID")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value."""
        valid_statuses = ["active", "planned", "retired", "staging", "decommissioning"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class SiteCreate(SiteBase):
    """Schema for creating a site."""

    @field_validator("slug", mode="before")
    @classmethod
    def auto_generate_slug(cls, v: str | None, info) -> str:
        """Auto-generate slug from name if not provided."""
        if v:
            return v
        name = info.data.get("name", "")
        return generate_slug(name) if name else ""


class SiteUpdate(BaseModel):
    """Schema for updating a site."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    status: str | None = None
    description: str | None = Field(None, max_length=500)
    tenant_id: int | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Validate status value."""
        if v is None:
            return v
        valid_statuses = ["active", "planned", "retired", "staging", "decommissioning"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class SiteResponse(SiteBase):
    """Schema for site response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    last_updated: datetime
