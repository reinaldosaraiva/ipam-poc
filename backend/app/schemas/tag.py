"""Tag schemas for API validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.slug import generate_slug


class TagBase(BaseModel):
    """Base schema for Tag."""

    name: str = Field(..., min_length=1, max_length=100, description="Tag name")
    slug: str | None = Field(None, max_length=100, description="URL-friendly slug")
    description: str = Field(default="", max_length=500, description="Tag description")
    color: str = Field(default="9e9e9e", max_length=6, description="Color hex code (without #)")


class TagCreate(TagBase):
    """Schema for creating a tag."""

    @field_validator("slug", mode="before")
    @classmethod
    def auto_generate_slug(cls, v: str | None, info) -> str:
        """Auto-generate slug from name if not provided."""
        if v:
            return v
        name = info.data.get("name", "")
        return generate_slug(name) if name else ""


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(None, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, max_length=6)


class TagResponse(TagBase):
    """Schema for tag response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created: datetime
    last_updated: datetime
