"""Sites API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.site import SiteCreate, SiteResponse, SiteUpdate
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/", response_model=list[SiteResponse])
async def list_sites(
    tenant_id: int | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[SiteResponse]:
    """List all sites with optional filtering."""
    nb = get_netbox_client()

    filters = {"limit": limit, "offset": offset}
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if status:
        filters["status"] = status

    sites = nb.dcim.sites.filter(**filters)

    return [
        SiteResponse(
            id=site.id,
            name=site.name,
            slug=site.slug,
            status=site.status.value if site.status else "active",
            description=site.description or "",
            tenant_id=site.tenant.id if site.tenant else None,
            created=site.created,
            last_updated=site.last_updated,
        )
        for site in sites
    ]


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(site_id: int) -> SiteResponse:
    """Get a specific site by ID."""
    nb = get_netbox_client()
    site = nb.dcim.sites.get(site_id)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with ID {site_id} not found",
        )

    return SiteResponse(
        id=site.id,
        name=site.name,
        slug=site.slug,
        status=site.status.value if site.status else "active",
        description=site.description or "",
        tenant_id=site.tenant.id if site.tenant else None,
        created=site.created,
        last_updated=site.last_updated,
    )


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(site_data: SiteCreate) -> SiteResponse:
    """Create a new site."""
    nb = get_netbox_client()

    # Auto-generate slug if not provided
    slug = site_data.slug or generate_slug(site_data.name)

    data = {
        "name": site_data.name,
        "slug": slug,
        "status": site_data.status,
        "description": site_data.description,
    }

    if site_data.tenant_id:
        data["tenant"] = site_data.tenant_id

    try:
        site = nb.dcim.sites.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return SiteResponse(
        id=site.id,
        name=site.name,
        slug=site.slug,
        status=site.status.value if site.status else "active",
        description=site.description or "",
        tenant_id=site.tenant.id if site.tenant else None,
        created=site.created,
        last_updated=site.last_updated,
    )


@router.patch("/{site_id}", response_model=SiteResponse)
async def update_site(site_id: int, site_data: SiteUpdate) -> SiteResponse:
    """Update an existing site."""
    nb = get_netbox_client()
    site = nb.dcim.sites.get(site_id)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with ID {site_id} not found",
        )

    update_data = site_data.model_dump(exclude_unset=True)

    if "tenant_id" in update_data:
        update_data["tenant"] = update_data.pop("tenant_id")

    try:
        site.update(update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh site data
    site = nb.dcim.sites.get(site_id)

    return SiteResponse(
        id=site.id,
        name=site.name,
        slug=site.slug,
        status=site.status.value if site.status else "active",
        description=site.description or "",
        tenant_id=site.tenant.id if site.tenant else None,
        created=site.created,
        last_updated=site.last_updated,
    )


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(site_id: int) -> None:
    """Delete a site."""
    nb = get_netbox_client()
    site = nb.dcim.sites.get(site_id)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with ID {site_id} not found",
        )

    try:
        site.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
