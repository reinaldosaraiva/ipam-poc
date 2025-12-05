"""Naming conventions for network resources.

Based on patterns from net-automation Terraform modules.
"""

import re
from dataclasses import dataclass
from enum import Enum

from app.utils.slug import generate_slug


class RegionCode(str, Enum):
    """Brazilian region codes."""

    NORDESTE = "ne"
    SUDESTE = "se"
    SUL = "s"
    NORTE = "n"
    CENTRO_OESTE = "co"


class ResourceType(str, Enum):
    """Resource type codes for naming."""

    DATACENTER = "dc"
    SITE = "site"
    TENANT = "tenant"
    RACK = "rack"
    DEVICE = "dev"
    INTERFACE = "iface"


@dataclass
class NamingConvention:
    """
    Naming convention rules for network resources.

    Patterns:
    - Site: "Site {Region}" → slug: "site-{region}"
    - Tenant: "br-{region}-{number}" (e.g., br-ne-1)
    - Facility: "{CITY}-DC-{NUMBER}" (e.g., RJ-DC-01, SP-DC-02)
    - VLAN: "VLAN {vid} - {description}"
    """

    @staticmethod
    def generate_site_name(region: str, city: str | None = None) -> str:
        """Generate site name following convention."""
        if city:
            return f"Site {city}"
        return f"Site {region.title()}"

    @staticmethod
    def generate_tenant_name(
        country: str = "br",
        region: str = "ne",
        number: int = 1,
    ) -> str:
        """
        Generate tenant name following convention.

        Format: {country}-{region}-{number}
        Example: br-ne-1
        """
        return f"{country}-{region}-{number}"

    @staticmethod
    def generate_facility_code(
        city_code: str,
        dc_number: int = 1,
    ) -> str:
        """
        Generate facility code following convention.

        Format: {CITY}-DC-{NUMBER}
        Example: RJ-DC-01, SP-DC-02
        """
        return f"{city_code.upper()}-DC-{dc_number:02d}"

    @staticmethod
    def generate_vlan_name(vid: int, description: str) -> str:
        """
        Generate VLAN name following convention.

        Format: VLAN {vid} - {description}
        Example: VLAN 100 - OOB/BMC
        """
        return f"VLAN {vid} - {description}"

    @staticmethod
    def generate_rack_name(
        site_code: str,
        row: str,
        number: int,
    ) -> str:
        """
        Generate rack name following convention.

        Format: {SITE}-{ROW}{NUMBER}
        Example: NE1-A01, SP1-B02
        """
        return f"{site_code.upper()}-{row.upper()}{number:02d}"

    @staticmethod
    def generate_device_name(
        role: str,
        site_code: str,
        number: int,
    ) -> str:
        """
        Generate device name following convention.

        Format: {role}-{site}-{number}
        Example: spine-ne1-01, leaf-sp1-02
        """
        return f"{role.lower()}-{site_code.lower()}-{number:02d}"

    @staticmethod
    def generate_interface_name(
        interface_type: str,
        number: int,
        slot: int | None = None,
    ) -> str:
        """
        Generate interface name following convention.

        Format: {type}{slot}/{number} or {type}{number}
        Example: Ethernet1/1, Management0
        """
        if slot is not None:
            return f"{interface_type}{slot}/{number}"
        return f"{interface_type}{number}"

    @staticmethod
    def parse_tenant_name(name: str) -> dict[str, str | int] | None:
        """
        Parse tenant name to extract components.

        Returns: {"country": "br", "region": "ne", "number": 1}
        """
        pattern = r"^([a-z]{2})-([a-z]{1,2})-(\d+)$"
        match = re.match(pattern, name.lower())
        if match:
            return {
                "country": match.group(1),
                "region": match.group(2),
                "number": int(match.group(3)),
            }
        return None

    @staticmethod
    def parse_facility_code(code: str) -> dict[str, str | int] | None:
        """
        Parse facility code to extract components.

        Returns: {"city_code": "RJ", "dc_number": 1}
        """
        pattern = r"^([A-Z]{2,4})-DC-(\d{2})$"
        match = re.match(pattern, code.upper())
        if match:
            return {
                "city_code": match.group(1),
                "dc_number": int(match.group(2)),
            }
        return None

    @staticmethod
    def validate_vlan_vid_range(vid: int, category: str) -> bool:
        """
        Validate VLAN ID is within expected range for category.

        Categories:
        - management: 100-199
        - data: 250-299
        """
        ranges = {
            "management": (100, 199),
            "data": (250, 299),
        }
        if category not in ranges:
            return True  # No validation for unknown categories
        min_vid, max_vid = ranges[category]
        return min_vid <= vid <= max_vid
