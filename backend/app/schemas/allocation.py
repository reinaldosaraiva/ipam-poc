"""Allocation schemas for API validation."""

from pydantic import BaseModel, Field


class VlanDefinitionResponse(BaseModel):
    """Predefined VLAN definition response."""

    vid: int
    name: str
    description: str
    category: str


class VlanRangeResponse(BaseModel):
    """VLAN range response."""

    category: str
    start: int
    end: int
    description: str


class PrefixAllocationRequest(BaseModel):
    """Request for prefix allocation."""

    base_network: str = Field(..., description="Base network (e.g., '10.0')")
    site_id: int | None = Field(None, description="Site ID to associate prefixes")
    tenant_id: int | None = Field(None, description="Tenant ID to associate prefixes")
    rack_count: int = Field(default=20, ge=1, le=50, description="Number of racks")
    create_vlans: bool = Field(default=True, description="Also create VLANs")
    dry_run: bool = Field(default=False, description="Preview without creating")


class PrefixAllocationResponse(BaseModel):
    """Single prefix allocation response."""

    prefix: str
    description: str
    vlan_vid: int | None = None
    is_container: bool = False
    parent_prefix: str | None = None
    status: str = "pending"


class AllocationPlanResponse(BaseModel):
    """Complete allocation plan response."""

    base_network: str
    container_prefix: str
    vlan_subnets: list[PrefixAllocationResponse]
    host_subnets: list[PrefixAllocationResponse]
    vlans_to_create: list[VlanDefinitionResponse]
    total_prefixes: int
    total_vlans: int


class SiteAllocationRequest(BaseModel):
    """Request for complete site allocation."""

    site_name: str = Field(..., description="Site name (e.g., 'Site Nordeste')")
    region_code: str = Field(..., description="Region code (e.g., 'ne', 'se')")
    base_network: str = Field(..., description="Base network (e.g., '10.0')")
    facility_code: str | None = Field(None, description="Facility code (e.g., 'NE-DC-01')")
    tenant_name: str | None = Field(None, description="Tenant name (auto-generated if not provided)")
    rack_count: int = Field(default=20, ge=1, le=50, description="Number of racks")
    dry_run: bool = Field(default=False, description="Preview without creating")


class SiteAllocationResponse(BaseModel):
    """Complete site allocation response."""

    site: dict
    tenant: dict | None
    allocation_plan: AllocationPlanResponse
    created: bool
