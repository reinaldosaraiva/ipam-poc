"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.prefix import PrefixCreate, PrefixStatus, PrefixUpdate
from app.schemas.vlan import VlanCreate
from app.schemas.device import DeviceCreate


class TestPrefixSchemas:
    """Tests for Prefix schemas."""

    def test_prefix_create_valid(self):
        """Test valid prefix creation."""
        data = PrefixCreate(
            prefix="10.0.0.0/24",
            status=PrefixStatus.ACTIVE,
            description="Test prefix",
        )
        assert data.prefix == "10.0.0.0/24"
        assert data.status == PrefixStatus.ACTIVE

    def test_prefix_create_invalid_cidr(self):
        """Test that invalid CIDR raises validation error."""
        with pytest.raises(ValidationError):
            PrefixCreate(prefix="not-a-cidr")

    def test_prefix_create_valid_ipv6(self):
        """Test valid IPv6 prefix."""
        data = PrefixCreate(prefix="2001:db8::/32")
        assert data.prefix == "2001:db8::/32"

    def test_prefix_create_defaults(self):
        """Test default values for prefix creation."""
        data = PrefixCreate(prefix="192.168.0.0/16")
        assert data.status == PrefixStatus.ACTIVE
        assert data.is_pool is False
        assert data.tags == []

    def test_prefix_update_partial(self):
        """Test partial update schema."""
        data = PrefixUpdate(status=PrefixStatus.RESERVED)
        assert data.status == PrefixStatus.RESERVED
        assert data.description is None


class TestVlanSchemas:
    """Tests for VLAN schemas."""

    def test_vlan_create_valid(self):
        """Test valid VLAN creation."""
        data = VlanCreate(name="VLAN100", vid=100)
        assert data.name == "VLAN100"
        assert data.vid == 100

    def test_vlan_create_invalid_vid_low(self):
        """Test that VID < 1 raises validation error."""
        with pytest.raises(ValidationError):
            VlanCreate(name="Invalid", vid=0)

    def test_vlan_create_invalid_vid_high(self):
        """Test that VID > 4094 raises validation error."""
        with pytest.raises(ValidationError):
            VlanCreate(name="Invalid", vid=4095)


class TestDeviceSchemas:
    """Tests for Device schemas."""

    def test_device_create_valid(self):
        """Test valid device creation."""
        data = DeviceCreate(
            name="switch-01",
            device_type_id=1,
            role_id=1,
            site_id=1,
        )
        assert data.name == "switch-01"

    def test_device_create_empty_name(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError):
            DeviceCreate(
                name="",
                device_type_id=1,
                role_id=1,
                site_id=1,
            )
