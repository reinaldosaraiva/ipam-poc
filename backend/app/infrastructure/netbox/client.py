"""NetBox API Client using pynetbox."""

from functools import lru_cache

import pynetbox
from pynetbox.core.api import Api

from app.config import get_settings


class NetBoxClient:
    """Wrapper around pynetbox for NetBox API interactions."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api: Api = pynetbox.api(
            url=settings.netbox_url,
            token=settings.netbox_token,
        )
        # Disable SSL verification for development
        self._api.http_session.verify = False

    @property
    def ipam(self):
        """Access IPAM endpoints (prefixes, vlans, etc.)."""
        return self._api.ipam

    @property
    def dcim(self):
        """Access DCIM endpoints (devices, interfaces, etc.)."""
        return self._api.dcim

    @property
    def tenancy(self):
        """Access Tenancy endpoints."""
        return self._api.tenancy

    def get_prefix(self, prefix_id: int):
        """Get a single prefix by ID."""
        return self.ipam.prefixes.get(prefix_id)

    def list_prefixes(self, **filters):
        """List prefixes with optional filters."""
        return self.ipam.prefixes.filter(**filters)

    def create_prefix(self, data: dict):
        """Create a new prefix."""
        return self.ipam.prefixes.create(data)

    def update_prefix(self, prefix_id: int, data: dict):
        """Update an existing prefix."""
        prefix = self.get_prefix(prefix_id)
        if prefix:
            return prefix.update(data)
        return None

    def delete_prefix(self, prefix_id: int) -> bool:
        """Delete a prefix."""
        prefix = self.get_prefix(prefix_id)
        if prefix:
            return prefix.delete()
        return False


@lru_cache
def get_netbox_client() -> NetBoxClient:
    """Get cached NetBox client instance."""
    return NetBoxClient()
