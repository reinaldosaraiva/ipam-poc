"""FastAPI Application Entry Point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import prefixes, vlans, devices, sites, tenants, vlan_groups, device_roles, tags, allocation
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - IPAM
app.include_router(prefixes.router, prefix="/api/v1/prefixes", tags=["IPAM - Prefixes"])
app.include_router(vlans.router, prefix="/api/v1/vlans", tags=["IPAM - VLANs"])
app.include_router(vlan_groups.router, prefix="/api/v1/vlan-groups", tags=["IPAM - VLAN Groups"])

# Include routers - DCIM
app.include_router(sites.router, prefix="/api/v1/sites", tags=["DCIM - Sites"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["DCIM - Devices"])
app.include_router(device_roles.router, prefix="/api/v1/device-roles", tags=["DCIM - Device Roles"])

# Include routers - Tenancy
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenancy"])

# Include routers - Extras
app.include_router(tags.router, prefix="/api/v1/tags", tags=["Extras - Tags"])

# Include routers - Allocation
app.include_router(allocation.router, prefix="/api/v1/allocation", tags=["Allocation"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}
