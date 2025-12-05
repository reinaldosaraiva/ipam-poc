"""VLAN Groups API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.vlan_group import VlanGroupCreate, VlanGroupResponse, VlanGroupUpdate
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/", response_model=list[VlanGroupResponse])
async def list_vlan_groups(
    limit: int = 100,
    offset: int = 0,
) -> list[VlanGroupResponse]:
    """List all VLAN groups."""
    nb = get_netbox_client()

    groups = nb.ipam.vlan_groups.filter(limit=limit, offset=offset)

    return [
        VlanGroupResponse(
            id=group.id,
            name=group.name,
            slug=group.slug,
            description=group.description or "",
            vid_ranges=str(group.vid_ranges) if group.vid_ranges else None,
            tags=[tag.name for tag in group.tags] if group.tags else [],
            created=group.created,
            last_updated=group.last_updated,
        )
        for group in groups
    ]


@router.get("/{group_id}", response_model=VlanGroupResponse)
async def get_vlan_group(group_id: int) -> VlanGroupResponse:
    """Get a specific VLAN group by ID."""
    nb = get_netbox_client()
    group = nb.ipam.vlan_groups.get(group_id)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN Group with ID {group_id} not found",
        )

    return VlanGroupResponse(
        id=group.id,
        name=group.name,
        slug=group.slug,
        description=group.description or "",
        vid_ranges=str(group.vid_ranges) if group.vid_ranges else None,
        tags=[tag.name for tag in group.tags] if group.tags else [],
        created=group.created,
        last_updated=group.last_updated,
    )


@router.post("/", response_model=VlanGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_vlan_group(group_data: VlanGroupCreate) -> VlanGroupResponse:
    """Create a new VLAN group."""
    nb = get_netbox_client()

    slug = group_data.slug or generate_slug(group_data.name)

    data = {
        "name": group_data.name,
        "slug": slug,
        "description": group_data.description,
    }

    if group_data.vid_ranges:
        data["vid_ranges"] = group_data.vid_ranges
    if group_data.tags:
        data["tags"] = group_data.tags

    try:
        group = nb.ipam.vlan_groups.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return VlanGroupResponse(
        id=group.id,
        name=group.name,
        slug=group.slug,
        description=group.description or "",
        vid_ranges=str(group.vid_ranges) if group.vid_ranges else None,
        tags=[tag.name for tag in group.tags] if group.tags else [],
        created=group.created,
        last_updated=group.last_updated,
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vlan_group(group_id: int) -> None:
    """Delete a VLAN group."""
    nb = get_netbox_client()
    group = nb.ipam.vlan_groups.get(group_id)

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"VLAN Group with ID {group_id} not found",
        )

    try:
        group.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
