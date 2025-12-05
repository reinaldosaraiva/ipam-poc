"""Service layer for IP Prefix operations."""

from datetime import datetime

from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.prefix import (
    PrefixCreate,
    PrefixUpdate,
    PrefixResponse,
    NestedSite,
    NestedTenant,
)


class PrefixService:
    """Business logic for IP Prefix management."""

    def __init__(self) -> None:
        self.client = get_netbox_client()

    def _to_response(self, prefix) -> PrefixResponse:
        """Convert NetBox prefix object to response schema."""
        site = None
        if prefix.site:
            site = NestedSite(id=prefix.site.id, name=prefix.site.name)

        tenant = None
        if prefix.tenant:
            tenant = NestedTenant(id=prefix.tenant.id, name=prefix.tenant.name)

        return PrefixResponse(
            id=prefix.id,
            prefix=str(prefix.prefix),
            status=prefix.status.value if prefix.status else "active",
            description=prefix.description,
            site_id=prefix.site.id if prefix.site else None,
            tenant_id=prefix.tenant.id if prefix.tenant else None,
            vlan_id=prefix.vlan.id if prefix.vlan else None,
            role_id=prefix.role.id if prefix.role else None,
            is_pool=prefix.is_pool,
            tags=[str(t) for t in (prefix.tags or [])],
            site=site,
            tenant=tenant,
            created=datetime.fromisoformat(str(prefix.created)),
            last_updated=datetime.fromisoformat(str(prefix.last_updated)),
        )

    async def list_prefixes(
        self,
        site_id: int | None = None,
        tenant_id: int | None = None,
        status: str | None = None,
        tag: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PrefixResponse]:
        """List prefixes with filtering."""
        filters = {}
        if site_id:
            filters["site_id"] = site_id
        if tenant_id:
            filters["tenant_id"] = tenant_id
        if status:
            filters["status"] = status
        if tag:
            filters["tag"] = tag

        filters["limit"] = limit
        filters["offset"] = offset

        prefixes = self.client.list_prefixes(**filters)
        return [self._to_response(p) for p in prefixes]

    async def get_prefix(self, prefix_id: int) -> PrefixResponse | None:
        """Get a single prefix by ID."""
        prefix = self.client.get_prefix(prefix_id)
        if prefix:
            return self._to_response(prefix)
        return None

    async def create_prefix(self, data: PrefixCreate) -> PrefixResponse:
        """Create a new prefix."""
        payload = {
            "prefix": data.prefix,
            "status": data.status.value,
            "description": data.description,
            "site": data.site_id,
            "tenant": data.tenant_id,
            "vlan": data.vlan_id,
            "role": data.role_id,
            "is_pool": data.is_pool,
            "tags": data.tags,
        }
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        prefix = self.client.create_prefix(payload)
        return self._to_response(prefix)

    async def update_prefix(
        self, prefix_id: int, data: PrefixUpdate
    ) -> PrefixResponse | None:
        """Update an existing prefix."""
        payload = data.model_dump(exclude_unset=True)
        if "status" in payload and payload["status"]:
            payload["status"] = payload["status"].value

        prefix = self.client.update_prefix(prefix_id, payload)
        if prefix:
            return self._to_response(prefix)
        return None

    async def delete_prefix(self, prefix_id: int) -> bool:
        """Delete a prefix."""
        return self.client.delete_prefix(prefix_id)
