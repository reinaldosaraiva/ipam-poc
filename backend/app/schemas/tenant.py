"""Tenant schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.slug import generate_slug


class TenantBase(BaseModel):
    """Base schema for Tenant."""

    name: str = Field(..., min_length=1, max_length=100, description="Tenant name")
    slug: str | None = Field(None, max_length=100, description="URL-friendly slug")
    description: str = Field(default="", max_length=500, description="Tenant description")
    group_id: int | None = Field(None, description="Associated tenant group ID")
    tags: list[str] = Field(default_factory=list, description="Associated tags")


class TenantCreate(TenantBase):
    """Schema for creating a tenant."""

    @field_validator("slug", mode="before")
    @classmethod
    def auto_generate_slug(cls, v: str | None, info) -> str:
        """Auto-generate slug from name if not provided."""
        if v:
            return v
        name = info.data.get("name", "")
        return generate_slug(name) if name else ""


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    group_id: int | None = None
    tags: list[str] | None = None


class TenantResponse(TenantBase):
    """Schema for tenant response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    last_updated: datetime
