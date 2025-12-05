"""Allocation API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.domain.allocation.naming import NamingConvention
from app.domain.allocation.rules import AllocationRules, VlanCategory
from app.infrastructure.netbox.client import get_netbox_client
from app.schemas.allocation import (
    AllocationPlanResponse,
    PrefixAllocationRequest,
    PrefixAllocationResponse,
    SiteAllocationRequest,
    SiteAllocationResponse,
    VlanDefinitionResponse,
    VlanRangeResponse,
)
from app.utils.slug import generate_slug

router = APIRouter()


@router.get("/vlan-definitions", response_model=list[VlanDefinitionResponse])
async def get_vlan_definitions() -> list[VlanDefinitionResponse]:
    """Get all predefined VLAN definitions."""
    return [
        VlanDefinitionResponse(
            vid=vlan.vid,
            name=vlan.name,
            description=vlan.description,
            category=vlan.category.value,
        )
        for vlan in AllocationRules.VLAN_DEFINITIONS
    ]


@router.get("/vlan-ranges", response_model=list[VlanRangeResponse])
async def get_vlan_ranges() -> list[VlanRangeResponse]:
    """Get VLAN ranges by category."""
    return [
        VlanRangeResponse(
            category=category.value,
            start=vlan_range.start,
            end=vlan_range.end,
            description=vlan_range.description,
        )
        for category, vlan_range in AllocationRules.VLAN_RANGES.items()
    ]


@router.post("/plan", response_model=AllocationPlanResponse)
async def create_allocation_plan(
    request: PrefixAllocationRequest,
) -> AllocationPlanResponse:
    """
    Generate an allocation plan for prefixes and VLANs.

    This endpoint calculates all prefixes and VLANs that would be created
    based on the allocation rules without actually creating them.
    """
    # Generate container and VLAN subnets
    vlan_subnets = []
    container_prefix = ""

    for allocation in AllocationRules.generate_vlan_subnets(request.base_network):
        if allocation.is_container:
            container_prefix = allocation.prefix
        else:
            vlan_subnets.append(
                PrefixAllocationResponse(
                    prefix=allocation.prefix,
                    description=allocation.description,
                    vlan_vid=allocation.vlan_vid,
                    is_container=allocation.is_container,
                    parent_prefix=allocation.parent_prefix,
                )
            )

    # Generate host subnets for each VLAN subnet
    host_subnets = []
    for vlan_subnet in vlan_subnets:
        for host in AllocationRules.generate_host_subnets(
            vlan_subnet.prefix, request.rack_count
        ):
            host_subnets.append(
                PrefixAllocationResponse(
                    prefix=host.prefix,
                    description=host.description,
                    parent_prefix=host.parent_prefix,
                )
            )

    # VLAN definitions to create
    vlans_to_create = [
        VlanDefinitionResponse(
            vid=vlan.vid,
            name=vlan.name,
            description=vlan.description,
            category=vlan.category.value,
        )
        for vlan in AllocationRules.VLAN_DEFINITIONS
    ]

    return AllocationPlanResponse(
        base_network=request.base_network,
        container_prefix=container_prefix,
        vlan_subnets=vlan_subnets,
        host_subnets=host_subnets,
        vlans_to_create=vlans_to_create if request.create_vlans else [],
        total_prefixes=1 + len(vlan_subnets) + len(host_subnets),  # container + vlan + host
        total_vlans=len(vlans_to_create) if request.create_vlans else 0,
    )


@router.post("/execute", response_model=AllocationPlanResponse)
async def execute_allocation(
    request: PrefixAllocationRequest,
) -> AllocationPlanResponse:
    """
    Execute the allocation plan, creating prefixes and VLANs in NetBox.

    This endpoint creates all resources based on the allocation rules.
    """
    if request.dry_run:
        return await create_allocation_plan(request)

    nb = get_netbox_client()

    # First, generate the plan
    plan = await create_allocation_plan(request)

    try:
        # Create container prefix
        nb.ipam.prefixes.create({
            "prefix": plan.container_prefix,
            "status": "container",
            "description": f"Container prefix for {request.base_network}",
            "site": request.site_id,
            "tenant": request.tenant_id,
        })

        # Create VLANs if requested
        vlan_id_map = {}
        if request.create_vlans:
            for vlan_def in plan.vlans_to_create:
                vlan = nb.ipam.vlans.create({
                    "vid": vlan_def.vid,
                    "name": NamingConvention.generate_vlan_name(vlan_def.vid, vlan_def.name),
                    "status": "active",
                    "description": vlan_def.description,
                    "site": request.site_id,
                    "tenant": request.tenant_id,
                })
                vlan_id_map[vlan_def.vid] = vlan.id

        # Create VLAN subnets
        for subnet in plan.vlan_subnets:
            nb.ipam.prefixes.create({
                "prefix": subnet.prefix,
                "status": "active",
                "description": subnet.description,
                "site": request.site_id,
                "tenant": request.tenant_id,
                "vlan": vlan_id_map.get(subnet.vlan_vid) if subnet.vlan_vid else None,
            })

        # Create host subnets
        for host in plan.host_subnets:
            nb.ipam.prefixes.create({
                "prefix": host.prefix,
                "status": "active",
                "description": host.description,
                "site": request.site_id,
                "tenant": request.tenant_id,
            })

        # Update status to created
        for subnet in plan.vlan_subnets:
            subnet.status = "created"
        for host in plan.host_subnets:
            host.status = "created"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to execute allocation: {e}",
        )

    return plan


@router.post("/site", response_model=SiteAllocationResponse)
async def allocate_site(
    request: SiteAllocationRequest,
) -> SiteAllocationResponse:
    """
    Allocate a complete site with tenant, VLANs, and prefixes.

    This is the main entry point for creating a new site following
    all naming conventions and allocation patterns.
    """
    nb = get_netbox_client()

    # Generate names using conventions
    tenant_name = request.tenant_name or NamingConvention.generate_tenant_name(
        country="br",
        region=request.region_code,
        number=1,
    )
    facility_code = request.facility_code or NamingConvention.generate_facility_code(
        city_code=request.region_code.upper(),
        dc_number=1,
    )

    site_data = {
        "name": request.site_name,
        "slug": generate_slug(request.site_name),
        "status": "planned",
        "description": f"Data center {request.site_name} - {facility_code}",
    }
    tenant_data = {
        "name": tenant_name,
        "slug": generate_slug(tenant_name),
        "description": f"Tenant for {request.site_name}",
    }

    if request.dry_run:
        # Generate plan without creating
        allocation_plan = await create_allocation_plan(
            PrefixAllocationRequest(
                base_network=request.base_network,
                rack_count=request.rack_count,
                create_vlans=True,
                dry_run=True,
            )
        )

        return SiteAllocationResponse(
            site=site_data,
            tenant=tenant_data,
            allocation_plan=allocation_plan,
            created=False,
        )

    try:
        # Create tenant
        tenant = nb.tenancy.tenants.create(tenant_data)
        tenant_data["id"] = tenant.id

        # Create site with tenant
        site_data["tenant"] = tenant.id
        site = nb.dcim.sites.create(site_data)
        site_data["id"] = site.id

        # Execute allocation
        allocation_plan = await execute_allocation(
            PrefixAllocationRequest(
                base_network=request.base_network,
                site_id=site.id,
                tenant_id=tenant.id,
                rack_count=request.rack_count,
                create_vlans=True,
                dry_run=False,
            )
        )

        return SiteAllocationResponse(
            site=site_data,
            tenant=tenant_data,
            allocation_plan=allocation_plan,
            created=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to allocate site: {e}",
        )


@router.get("/naming/preview")
async def preview_naming(
    site_name: str = "Site Nordeste",
    region_code: str = "ne",
    rack_count: int = 5,
) -> dict:
    """
    Preview naming conventions for a site.

    Returns examples of all generated names following conventions.
    """
    return {
        "site": {
            "name": site_name,
            "slug": generate_slug(site_name),
        },
        "tenant": {
            "name": NamingConvention.generate_tenant_name("br", region_code, 1),
            "slug": generate_slug(NamingConvention.generate_tenant_name("br", region_code, 1)),
        },
        "facility_code": NamingConvention.generate_facility_code(region_code.upper(), 1),
        "vlans": [
            {
                "vid": vlan.vid,
                "name": NamingConvention.generate_vlan_name(vlan.vid, vlan.name),
                "category": vlan.category.value,
            }
            for vlan in AllocationRules.VLAN_DEFINITIONS[:4]  # Show first 4 as example
        ],
        "racks": [
            NamingConvention.generate_rack_name(region_code.upper() + "1", "A", i)
            for i in range(1, min(rack_count + 1, 6))
        ],
        "devices": {
            "spine": NamingConvention.generate_device_name("spine", region_code + "1", 1),
            "leaf": NamingConvention.generate_device_name("leaf", region_code + "1", 1),
        },
    }
