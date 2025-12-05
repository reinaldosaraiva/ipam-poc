"""API routes for IP Prefix management."""

from fastapi import APIRouter, HTTPException, Query
from app.schemas.prefix import PrefixCreate, PrefixUpdate, PrefixResponse
from app.domain.services.prefix_service import PrefixService

router = APIRouter()


@router.get("/", response_model=list[PrefixResponse])
async def list_prefixes(
    site_id: int | None = Query(None, description="Filter by site"),
    tenant_id: int | None = Query(None, description="Filter by tenant"),
    status: str | None = Query(None, description="Filter by status"),
    tag: str | None = Query(None, description="Filter by tag"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[PrefixResponse]:
    """List all IP prefixes with optional filtering."""
    service = PrefixService()
    return await service.list_prefixes(
        site_id=site_id,
        tenant_id=tenant_id,
        status=status,
        tag=tag,
        limit=limit,
        offset=offset,
    )


@router.get("/{prefix_id}", response_model=PrefixResponse)
async def get_prefix(prefix_id: int) -> PrefixResponse:
    """Get a specific IP prefix by ID."""
    service = PrefixService()
    prefix = await service.get_prefix(prefix_id)
    if not prefix:
        raise HTTPException(status_code=404, detail="Prefix not found")
    return prefix


@router.post("/", response_model=PrefixResponse, status_code=201)
async def create_prefix(data: PrefixCreate) -> PrefixResponse:
    """Create a new IP prefix."""
    service = PrefixService()
    return await service.create_prefix(data)


@router.patch("/{prefix_id}", response_model=PrefixResponse)
async def update_prefix(prefix_id: int, data: PrefixUpdate) -> PrefixResponse:
    """Update an existing IP prefix."""
    service = PrefixService()
    prefix = await service.update_prefix(prefix_id, data)
    if not prefix:
        raise HTTPException(status_code=404, detail="Prefix not found")
    return prefix


@router.delete("/{prefix_id}", status_code=204)
async def delete_prefix(prefix_id: int) -> None:
    """Delete an IP prefix."""
    service = PrefixService()
    deleted = await service.delete_prefix(prefix_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Prefix not found")
