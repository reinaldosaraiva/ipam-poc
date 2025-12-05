"""Tenants API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.tenant import TenantCreate, TenantResponse, TenantUpdate
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/", response_model=list[TenantResponse])
async def list_tenants(
    group_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[TenantResponse]:
    """List all tenants with optional filtering."""
    nb = get_netbox_client()

    filters = {"limit": limit, "offset": offset}
    if group_id:
        filters["group_id"] = group_id

    tenants = nb.tenancy.tenants.filter(**filters)

    return [
        TenantResponse(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            description=tenant.description or "",
            group_id=tenant.group.id if tenant.group else None,
            tags=[tag.name for tag in tenant.tags] if tenant.tags else [],
            created=tenant.created,
            last_updated=tenant.last_updated,
        )
        for tenant in tenants
    ]


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(tenant_id: int) -> TenantResponse:
    """Get a specific tenant by ID."""
    nb = get_netbox_client()
    tenant = nb.tenancy.tenants.get(tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {tenant_id} not found",
        )

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        description=tenant.description or "",
        group_id=tenant.group.id if tenant.group else None,
        tags=[tag.name for tag in tenant.tags] if tenant.tags else [],
        created=tenant.created,
        last_updated=tenant.last_updated,
    )


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(tenant_data: TenantCreate) -> TenantResponse:
    """Create a new tenant."""
    nb = get_netbox_client()

    # Auto-generate slug if not provided
    slug = tenant_data.slug or generate_slug(tenant_data.name)

    data = {
        "name": tenant_data.name,
        "slug": slug,
        "description": tenant_data.description,
    }

    if tenant_data.group_id:
        data["group"] = tenant_data.group_id
    if tenant_data.tags:
        data["tags"] = tenant_data.tags

    try:
        tenant = nb.tenancy.tenants.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        description=tenant.description or "",
        group_id=tenant.group.id if tenant.group else None,
        tags=[tag.name for tag in tenant.tags] if tenant.tags else [],
        created=tenant.created,
        last_updated=tenant.last_updated,
    )


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: int, tenant_data: TenantUpdate) -> TenantResponse:
    """Update an existing tenant."""
    nb = get_netbox_client()
    tenant = nb.tenancy.tenants.get(tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {tenant_id} not found",
        )

    update_data = tenant_data.model_dump(exclude_unset=True)

    if "group_id" in update_data:
        update_data["group"] = update_data.pop("group_id")

    try:
        tenant.update(update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh tenant data
    tenant = nb.tenancy.tenants.get(tenant_id)

    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        description=tenant.description or "",
        group_id=tenant.group.id if tenant.group else None,
        tags=[tag.name for tag in tenant.tags] if tenant.tags else [],
        created=tenant.created,
        last_updated=tenant.last_updated,
    )


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(tenant_id: int) -> None:
    """Delete a tenant."""
    nb = get_netbox_client()
    tenant = nb.tenancy.tenants.get(tenant_id)

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant with ID {tenant_id} not found",
        )

    try:
        tenant.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
