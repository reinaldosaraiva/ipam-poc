"""API routes for Device management."""

from fastapi import APIRouter, HTTPException, Query, status

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse

router = APIRouter()


@router.get("/", response_model=list[DeviceResponse])
async def list_devices(
    site_id: int | None = Query(None),
    role_id: int | None = Query(None),
    device_status: str | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[DeviceResponse]:
    """List all devices with optional filtering."""
    nb = get_netbox_client()

    filters = {"limit": limit, "offset": offset}
    if site_id:
        filters["site_id"] = site_id
    if role_id:
        filters["role_id"] = role_id
    if device_status:
        filters["status"] = device_status

    devices = nb.dcim.devices.filter(**filters)

    return [
        DeviceResponse(
            id=device.id,
            name=device.name,
            device_type_id=device.device_type.id if device.device_type else None,
            device_type_name=device.device_type.model if device.device_type else None,
            role_id=device.role.id if device.role else None,
            role_name=device.role.name if device.role else None,
            site_id=device.site.id if device.site else None,
            site_name=device.site.name if device.site else None,
            status=device.status.value if device.status else "active",
            serial=device.serial or "",
            description=device.description or "",
            tags=[tag.name for tag in device.tags] if device.tags else [],
            created=device.created,
            last_updated=device.last_updated,
        )
        for device in devices
    ]


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: int) -> DeviceResponse:
    """Get a specific device by ID."""
    nb = get_netbox_client()
    device = nb.dcim.devices.get(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    return DeviceResponse(
        id=device.id,
        name=device.name,
        device_type_id=device.device_type.id if device.device_type else None,
        device_type_name=device.device_type.model if device.device_type else None,
        role_id=device.role.id if device.role else None,
        role_name=device.role.name if device.role else None,
        site_id=device.site.id if device.site else None,
        site_name=device.site.name if device.site else None,
        status=device.status.value if device.status else "active",
        serial=device.serial or "",
        description=device.description or "",
        tags=[tag.name for tag in device.tags] if device.tags else [],
        created=device.created,
        last_updated=device.last_updated,
    )


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(data: DeviceCreate) -> DeviceResponse:
    """Create a new device."""
    nb = get_netbox_client()

    device_data = {
        "name": data.name,
        "device_type": data.device_type_id,
        "role": data.role_id,
        "site": data.site_id,
        "status": data.status,
    }

    if data.serial:
        device_data["serial"] = data.serial
    if data.description:
        device_data["description"] = data.description
    if data.tags:
        device_data["tags"] = data.tags

    try:
        device = nb.dcim.devices.create(device_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return DeviceResponse(
        id=device.id,
        name=device.name,
        device_type_id=device.device_type.id if device.device_type else None,
        device_type_name=device.device_type.model if device.device_type else None,
        role_id=device.role.id if device.role else None,
        role_name=device.role.name if device.role else None,
        site_id=device.site.id if device.site else None,
        site_name=device.site.name if device.site else None,
        status=device.status.value if device.status else "active",
        serial=device.serial or "",
        description=device.description or "",
        tags=[tag.name for tag in device.tags] if device.tags else [],
        created=device.created,
        last_updated=device.last_updated,
    )


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(device_id: int, data: DeviceUpdate) -> DeviceResponse:
    """Update an existing device."""
    nb = get_netbox_client()
    device = nb.dcim.devices.get(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "device_type_id" in update_data:
        update_data["device_type"] = update_data.pop("device_type_id")
    if "role_id" in update_data:
        update_data["role"] = update_data.pop("role_id")
    if "site_id" in update_data:
        update_data["site"] = update_data.pop("site_id")

    try:
        device.update(update_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh
    device = nb.dcim.devices.get(device_id)

    return DeviceResponse(
        id=device.id,
        name=device.name,
        device_type_id=device.device_type.id if device.device_type else None,
        device_type_name=device.device_type.model if device.device_type else None,
        role_id=device.role.id if device.role else None,
        role_name=device.role.name if device.role else None,
        site_id=device.site.id if device.site else None,
        site_name=device.site.name if device.site else None,
        status=device.status.value if device.status else "active",
        serial=device.serial or "",
        description=device.description or "",
        tags=[tag.name for tag in device.tags] if device.tags else [],
        created=device.created,
        last_updated=device.last_updated,
    )


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int) -> None:
    """Delete a device."""
    nb = get_netbox_client()
    device = nb.dcim.devices.get(device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found",
        )

    try:
        device.delete()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
