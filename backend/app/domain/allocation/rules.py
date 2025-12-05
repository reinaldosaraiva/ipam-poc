"""Allocation rules for IP prefixes and VLANs.

Based on patterns from net-automation Terraform modules.
"""

import ipaddress
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


class VlanCategory(str, Enum):
    """VLAN category types with predefined ranges."""

    MANAGEMENT = "management"  # 100-199
    DATA = "data"  # 250-299


@dataclass
class VlanRange:
    """VLAN range definition."""

    start: int
    end: int
    category: VlanCategory
    description: str


@dataclass
class VlanDefinition:
    """Predefined VLAN definition."""

    vid: int
    name: str
    description: str
    category: VlanCategory


@dataclass
class PrefixAllocation:
    """Prefix allocation result."""

    prefix: str
    description: str
    vlan_vid: int | None = None
    is_container: bool = False
    parent_prefix: str | None = None


class AllocationRules:
    """
    Allocation rules for network resources.

    VLAN Allocation Pattern:
    - Management Fabric: 100-199
      - 100: OOB/BMC
      - 101: PXE
      - 102: OAM
      - 103: BGP
    - Data Networks: 250-299
      - 250: Overlay
      - 251: API Internal
      - 252: API Access
      - 253: Block Storage
      - 254: Object Storage Access
      - 255: Object Storage Replicate
      - 256: Data Management

    Prefix Allocation Pattern:
    - Container: /16 (e.g., 10.0.0.0/16)
    - VLAN subnets: /21 per VLAN
    - Host subnets: /26 per rack
    """

    # Predefined VLAN definitions
    VLAN_DEFINITIONS: list[VlanDefinition] = [
        # Management Fabric (100-199)
        VlanDefinition(100, "oob_bmc", "OOB/BMC - Out-of-band management", VlanCategory.MANAGEMENT),
        VlanDefinition(101, "pxe", "PXE - Provisioning/boot network", VlanCategory.MANAGEMENT),
        VlanDefinition(102, "oam", "OAM - Operations, access, monitoring", VlanCategory.MANAGEMENT),
        VlanDefinition(103, "bgp", "BGP - Routing network", VlanCategory.MANAGEMENT),
        # Data Networks (250-299)
        VlanDefinition(250, "overlay", "Overlay - Tunneling network", VlanCategory.DATA),
        VlanDefinition(251, "api_internal", "API Internal - Service connectivity", VlanCategory.DATA),
        VlanDefinition(252, "api_access", "API Access - User to Kong", VlanCategory.DATA),
        VlanDefinition(253, "block_storage", "Block Storage - Ceph access/replication", VlanCategory.DATA),
        VlanDefinition(254, "object_storage_access", "Object Storage Access - Swift Proxy", VlanCategory.DATA),
        VlanDefinition(255, "object_storage_replicate", "Object Storage Replicate - Swift data", VlanCategory.DATA),
        VlanDefinition(256, "data_management", "Data Management - Telco rack management", VlanCategory.DATA),
    ]

    # VLAN ranges by category
    VLAN_RANGES: dict[VlanCategory, VlanRange] = {
        VlanCategory.MANAGEMENT: VlanRange(100, 199, VlanCategory.MANAGEMENT, "Management Fabric"),
        VlanCategory.DATA: VlanRange(250, 299, VlanCategory.DATA, "Data Networks"),
    }

    # Prefix sizes
    CONTAINER_PREFIX_SIZE = 16  # /16 for site container
    VLAN_SUBNET_SIZE = 21  # /21 per VLAN
    HOST_SUBNET_SIZE = 26  # /26 per rack

    @classmethod
    def get_vlan_definition(cls, vid: int) -> VlanDefinition | None:
        """Get predefined VLAN definition by VID."""
        for vlan in cls.VLAN_DEFINITIONS:
            if vlan.vid == vid:
                return vlan
        return None

    @classmethod
    def get_vlan_category(cls, vid: int) -> VlanCategory | None:
        """Determine VLAN category based on VID."""
        for category, vlan_range in cls.VLAN_RANGES.items():
            if vlan_range.start <= vid <= vlan_range.end:
                return category
        return None

    @classmethod
    def get_available_vlan_vid(cls, category: VlanCategory, used_vids: list[int]) -> int | None:
        """Get next available VLAN VID in category."""
        vlan_range = cls.VLAN_RANGES.get(category)
        if not vlan_range:
            return None

        for vid in range(vlan_range.start, vlan_range.end + 1):
            if vid not in used_vids:
                return vid
        return None

    @classmethod
    def calculate_container_prefix(cls, base_network: str) -> str:
        """
        Calculate container prefix from base network.

        Args:
            base_network: Base network (e.g., "10.0")

        Returns:
            Container prefix (e.g., "10.0.0.0/16")
        """
        return f"{base_network}.0.0/{cls.CONTAINER_PREFIX_SIZE}"

    @classmethod
    def calculate_vlan_subnet(
        cls,
        base_network: str,
        vlan_vid: int,
        subnet_offset: int,
    ) -> str:
        """
        Calculate VLAN subnet from base network.

        Args:
            base_network: Base network (e.g., "10.0")
            vlan_vid: VLAN ID
            subnet_offset: Subnet offset multiplier (0, 1, 2, ...)

        Returns:
            VLAN subnet (e.g., "10.0.8.0/21")
        """
        # Each /21 contains 2048 addresses, offset by 8 in the third octet
        third_octet = (subnet_offset + 1) * 8
        return f"{base_network}.{third_octet}.0/{cls.VLAN_SUBNET_SIZE}"

    @classmethod
    def generate_vlan_subnets(
        cls,
        base_network: str,
    ) -> Iterator[PrefixAllocation]:
        """
        Generate all VLAN subnets based on predefined VLANs.

        Args:
            base_network: Base network (e.g., "10.0")

        Yields:
            PrefixAllocation for each VLAN
        """
        container = cls.calculate_container_prefix(base_network)

        # Yield container first
        yield PrefixAllocation(
            prefix=container,
            description=f"Container prefix for {base_network}",
            is_container=True,
        )

        # Generate subnets for each predefined VLAN
        for idx, vlan in enumerate(cls.VLAN_DEFINITIONS):
            subnet = cls.calculate_vlan_subnet(base_network, vlan.vid, idx)
            yield PrefixAllocation(
                prefix=subnet,
                description=vlan.description,
                vlan_vid=vlan.vid,
                parent_prefix=container,
            )

    @classmethod
    def generate_host_subnets(
        cls,
        vlan_subnet: str,
        rack_count: int,
    ) -> Iterator[PrefixAllocation]:
        """
        Generate /26 host subnets for each rack within a VLAN subnet.

        Args:
            vlan_subnet: VLAN subnet (e.g., "10.0.8.0/21")
            rack_count: Number of racks

        Yields:
            PrefixAllocation for each rack subnet
        """
        network = ipaddress.ip_network(vlan_subnet)

        # A /21 can contain up to 32 /26 subnets
        host_subnets = list(network.subnets(new_prefix=cls.HOST_SUBNET_SIZE))

        for rack_num in range(1, min(rack_count + 1, len(host_subnets) + 1)):
            subnet = host_subnets[rack_num - 1]
            yield PrefixAllocation(
                prefix=str(subnet),
                description=f"Rack {rack_num:02d} subnet",
                parent_prefix=vlan_subnet,
            )

    @classmethod
    def validate_prefix_hierarchy(
        cls,
        parent: str,
        child: str,
    ) -> bool:
        """
        Validate that child prefix is within parent prefix.

        Args:
            parent: Parent prefix (e.g., "10.0.0.0/16")
            child: Child prefix (e.g., "10.0.8.0/21")

        Returns:
            True if child is within parent
        """
        try:
            parent_net = ipaddress.ip_network(parent)
            child_net = ipaddress.ip_network(child)
            return child_net.subnet_of(parent_net)
        except ValueError:
            return False

    @classmethod
    def get_next_available_prefix(
        cls,
        parent_prefix: str,
        prefix_length: int,
        used_prefixes: list[str],
    ) -> str | None:
        """
        Get next available prefix within parent.

        Args:
            parent_prefix: Parent prefix to allocate from
            prefix_length: Desired prefix length
            used_prefixes: List of already used prefixes

        Returns:
            Next available prefix or None if exhausted
        """
        try:
            parent = ipaddress.ip_network(parent_prefix)
            used = {ipaddress.ip_network(p) for p in used_prefixes}

            for subnet in parent.subnets(new_prefix=prefix_length):
                if subnet not in used:
                    # Also check if it overlaps with any used prefix
                    overlaps = any(
                        subnet.overlaps(u) or u.overlaps(subnet) for u in used
                    )
                    if not overlaps:
                        return str(subnet)
            return None
        except ValueError:
            return None
