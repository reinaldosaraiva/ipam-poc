"""Device Roles API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.device_role import DeviceRoleCreate, DeviceRoleResponse, DeviceRoleUpdate
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/", response_model=list[DeviceRoleResponse])
async def list_device_roles(
    limit: int = 100,
    offset: int = 0,
) -> list[DeviceRoleResponse]:
    """List all device roles."""
    nb = get_netbox_client()

    roles = nb.dcim.device_roles.filter(limit=limit, offset=offset)

    return [
        DeviceRoleResponse(
            id=role.id,
            name=role.name,
            slug=role.slug,
            description=role.description or "",
            color=role.color or "9e9e9e",
            vm_role=role.vm_role if hasattr(role, "vm_role") else False,
            created=role.created,
            last_updated=role.last_updated,
        )
        for role in roles
    ]


@router.get("/{role_id}", response_model=DeviceRoleResponse)
async def get_device_role(role_id: int) -> DeviceRoleResponse:
    """Get a specific device role by ID."""
    nb = get_netbox_client()
    role = nb.dcim.device_roles.get(role_id)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device Role with ID {role_id} not found",
        )

    return DeviceRoleResponse(
        id=role.id,
        name=role.name,
        slug=role.slug,
        description=role.description or "",
        color=role.color or "9e9e9e",
        vm_role=role.vm_role if hasattr(role, "vm_role") else False,
        created=role.created,
        last_updated=role.last_updated,
    )


@router.post("/", response_model=DeviceRoleResponse, status_code=status.HTTP_201_CREATED)
async def create_device_role(role_data: DeviceRoleCreate) -> DeviceRoleResponse:
    """Create a new device role."""
    nb = get_netbox_client()

    slug = role_data.slug or generate_slug(role_data.name)

    data = {
        "name": role_data.name,
        "slug": slug,
        "description": role_data.description,
        "color": role_data.color,
        "vm_role": role_data.vm_role,
    }

    try:
        role = nb.dcim.device_roles.create(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return DeviceRoleResponse(
        id=role.id,
        name=role.name,
        slug=role.slug,
        description=role.description or "",
        color=role.color or "9e9e9e",
        vm_role=role.vm_role if hasattr(role, "vm_role") else False,
        created=role.created,
        last_updated=role.last_updated,
    )


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device_role(role_id: int) -> None:
    """Delete a device role."""
    nb = get_netbox_client()
    role = nb.dcim.device_roles.get(role_id)

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device Role with ID {role_id} not found",
        )

    try:
        role.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
