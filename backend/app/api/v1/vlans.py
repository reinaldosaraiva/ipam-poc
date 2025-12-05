"""API routes for VLAN management."""

from fastapi import APIRouter, HTTPException, Query, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.vlan import VlanCreate, VlanUpdate, VlanResponse

router = APIRouter()


@router.get("/", response_model=list[VlanResponse])
async def list_vlans(
    site_id: int | None = Query(None),
    tenant_id: int | None = Query(None),
    group_id: int | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[VlanResponse]:
    """List all VLANs with optional filtering."""
    nb = get_netbox_client()

    filters = {"limit": limit, "offset": offset}
    if site_id:
        filters["site_id"] = site_id
    if tenant_id:
        filters["tenant_id"] = tenant_id
    if group_id:
        filters["group_id"] = group_id

    vlans = nb.ipam.vlans.filter(**filters)

    return [
        VlanResponse(
            id=vlan.id,
            name=vlan.name,
            vid=vlan.vid,
            status=vlan.status.value if vlan.status else "active",
            description=vlan.description or "",
            site_id=vlan.site.id if vlan.site else None,
            tenant_id=vlan.tenant.id if vlan.tenant else None,
            group_id=vlan.group.id if vlan.group else None,
            tags=[tag.name for tag in vlan.tags] if vlan.tags else [],
            created=vlan.created,
            last_updated=vlan.last_updated,
        )
        for vlan in vlans
    ]


@router.get("/{vlan_id}", response_model=VlanResponse)
async def get_vlan(vlan_id: int) -> VlanResponse:
    """Get a specific VLAN by ID."""
    nb = get_netbox_client()
    vlan = nb.ipam.vlans.get(vlan_id)

    if not vlan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN with ID {vlan_id} not found",
        )

    return VlanResponse(
        id=vlan.id,
        name=vlan.name,
        vid=vlan.vid,
        status=vlan.status.value if vlan.status else "active",
        description=vlan.description or "",
        site_id=vlan.site.id if vlan.site else None,
        tenant_id=vlan.tenant.id if vlan.tenant else None,
        group_id=vlan.group.id if vlan.group else None,
        tags=[tag.name for tag in vlan.tags] if vlan.tags else [],
        created=vlan.created,
        last_updated=vlan.last_updated,
    )


@router.post("/", response_model=VlanResponse, status_code=status.HTTP_201_CREATED)
async def create_vlan(data: VlanCreate) -> VlanResponse:
    """Create a new VLAN."""
    nb = get_netbox_client()

    vlan_data = {
        "name": data.name,
        "vid": data.vid,
        "status": data.status,
        "description": data.description or "",
    }

    if data.site_id:
        vlan_data["site"] = data.site_id
    if data.tenant_id:
        vlan_data["tenant"] = data.tenant_id
    if data.group_id:
        vlan_data["group"] = data.group_id
    if data.tags:
        vlan_data["tags"] = data.tags

    try:
        vlan = nb.ipam.vlans.create(vlan_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return VlanResponse(
        id=vlan.id,
        name=vlan.name,
        vid=vlan.vid,
        status=vlan.status.value if vlan.status else "active",
        description=vlan.description or "",
        site_id=vlan.site.id if vlan.site else None,
        tenant_id=vlan.tenant.id if vlan.tenant else None,
        group_id=vlan.group.id if vlan.group else None,
        tags=[tag.name for tag in vlan.tags] if vlan.tags else [],
        created=vlan.created,
        last_updated=vlan.last_updated,
    )


@router.patch("/{vlan_id}", response_model=VlanResponse)
async def update_vlan(vlan_id: int, data: VlanUpdate) -> VlanResponse:
    """Update an existing VLAN."""
    nb = get_netbox_client()
    vlan = nb.ipam.vlans.get(vlan_id)

    if not vlan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN with ID {vlan_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "site_id" in update_data:
        update_data["site"] = update_data.pop("site_id")
    if "tenant_id" in update_data:
        update_data["tenant"] = update_data.pop("tenant_id")
    if "group_id" in update_data:
        update_data["group"] = update_data.pop("group_id")

    try:
        vlan.update(update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh
    vlan = nb.ipam.vlans.get(vlan_id)

    return VlanResponse(
        id=vlan.id,
        name=vlan.name,
        vid=vlan.vid,
        status=vlan.status.value if vlan.status else "active",
        description=vlan.description or "",
        site_id=vlan.site.id if vlan.site else None,
        tenant_id=vlan.tenant.id if vlan.tenant else None,
        group_id=vlan.group.id if vlan.group else None,
        tags=[tag.name for tag in vlan.tags] if vlan.tags else [],
        created=vlan.created,
        last_updated=vlan.last_updated,
    )


@router.delete("/{vlan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vlan(vlan_id: int) -> None:
    """Delete a VLAN."""
    nb = get_netbox_client()
    vlan = nb.ipam.vlans.get(vlan_id)

    if not vlan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN with ID {vlan_id} not found",
        )

    try:
        vlan.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
