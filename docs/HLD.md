# IPAM Web Application - High-Level Design

> **Version:** 2.0
> **Date:** 2025-12-05
> **Status:** Implemented

---

## 1. Architecture Overview

The IPAM Web Application follows **Clean Architecture** with a hexagonal pattern, ensuring separation of concerns and modularity. The backend uses FastAPI with sync support for simplicity, while the frontend leverages Next.js 14 App Router for modern React patterns. All data integrates with NetBox via its REST API using pynetbox.

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                    Next.js 14 + React                        │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│   │Prefixes │ │  VLANs  │ │ Devices │ │Allocate │           │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                  FastAPI + Pydantic v2                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Routers   │→ │   Domain    │→ │   Infrastructure    │  │
│  │  (API v1)   │  │  (Services) │  │    (NetBox)         │  │
│  └─────────────┘  └─────────────┘  └──────────┬──────────┘  │
│         │                │                    │              │
│  ┌──────┴──────┐  ┌──────┴──────┐            │              │
│  │   Schemas   │  │ Allocation  │            │              │
│  │  (Pydantic) │  │   Rules     │            │              │
│  └─────────────┘  └─────────────┘            │              │
└──────────────────────────────────────────────┼──────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   NetBox    │
                                        │   REST API  │
                                        └─────────────┘
```

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | Next.js | 14.x | React framework with App Router |
| | TypeScript | 5.x | Type safety |
| | TailwindCSS | 3.x | Styling |
| **Backend** | FastAPI | 0.115+ | REST API framework |
| | Python | 3.11+ | Runtime |
| | Pydantic | 2.x | Data validation |
| | pynetbox | 7.x | NetBox SDK |
| **Infrastructure** | Docker | 24.x | Containerization |
| | Docker Compose | 2.x | Orchestration |
| | NetBox | 4.x | IPAM backend |

---

## 3. Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings with Pydantic
│   │
│   ├── api/                    # API Layer (Routers)
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependencies (NetBox client)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── prefixes.py     # /api/v1/prefixes - CRUD
│   │       ├── vlans.py        # /api/v1/vlans - CRUD
│   │       ├── devices.py      # /api/v1/devices - READ-ONLY
│   │       ├── sites.py        # /api/v1/sites - CRUD
│   │       ├── tenants.py      # /api/v1/tenants - CRUD
│   │       ├── interfaces.py   # /api/v1/interfaces - CRUD
│   │       └── allocation.py   # /api/v1/allocation - Provisioning
│   │
│   ├── domain/                 # Business Logic Layer
│   │   ├── __init__.py
│   │   └── allocation/
│   │       ├── __init__.py
│   │       ├── naming.py       # Naming conventions
│   │       └── rules.py        # Allocation rules (VLANs, prefixes)
│   │
│   ├── infrastructure/         # Data Access Layer
│   │   ├── __init__.py
│   │   └── netbox/
│   │       ├── __init__.py
│   │       └── client.py       # NetBox API client (pynetbox)
│   │
│   ├── schemas/                # Pydantic Schemas
│   │   ├── __init__.py
│   │   ├── prefix.py
│   │   ├── vlan.py
│   │   ├── device.py
│   │   ├── site.py
│   │   ├── tenant.py
│   │   └── allocation.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── slug.py             # Slug generation (Portuguese support)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── api/
│       └── test_prefixes.py
│
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

---

## 4. Frontend Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout with sidebar
│   ├── page.tsx                # Dashboard
│   ├── prefixes/
│   │   └── page.tsx            # Prefix management (CRUD)
│   ├── vlans/
│   │   └── page.tsx            # VLAN management (CRUD)
│   ├── devices/
│   │   └── page.tsx            # Device inventory (read-only sync)
│   ├── sites/
│   │   └── page.tsx            # Site management (CRUD)
│   ├── tenants/
│   │   └── page.tsx            # Tenant management (CRUD)
│   ├── allocation/
│   │   └── page.tsx            # Site allocation wizard
│   ├── interfaces/
│   │   └── page.tsx            # Interface management
│   └── settings/
│       └── page.tsx            # Settings
│
├── components/
│   ├── sidebar.tsx             # Navigation sidebar
│   └── ui/                     # UI components
│
├── lib/
│   └── api.ts                  # API client (fetch wrapper)
│
├── next.config.mjs
├── tailwind.config.ts
├── tsconfig.json
├── Dockerfile
└── package.json
```

---

## 5. Domain Model - Allocation

### 5.1 VLAN Allocation Rules

```python
class VlanRanges:
    MANAGEMENT = (100, 199)  # Management VLANs
    DATA = (250, 299)        # Data VLANs

PREDEFINED_VLANS = [
    # Management (100-199)
    {"vid": 100, "name": "vlan-mgmt", "category": "management"},
    {"vid": 101, "name": "vlan-oob", "category": "management"},
    {"vid": 102, "name": "vlan-bmc", "category": "management"},
    {"vid": 103, "name": "vlan-pxe", "category": "management"},
    # Data (250-299)
    {"vid": 250, "name": "vlan-k8s-nodes", "category": "data"},
    {"vid": 251, "name": "vlan-k8s-pods", "category": "data"},
    {"vid": 252, "name": "vlan-k8s-svc", "category": "data"},
    {"vid": 253, "name": "vlan-storage", "category": "data"},
    {"vid": 254, "name": "vlan-backup", "category": "data"},
    {"vid": 255, "name": "vlan-replication", "category": "data"},
    {"vid": 256, "name": "vlan-external", "category": "data"},
]
```

### 5.2 Prefix Allocation Hierarchy

```
Container (/16)
└── VLAN Subnets (/21)
    └── Host Subnets (/26)

Example for 10.0.0.0/16:
├── 10.0.0.0/21 (VLAN 100 - mgmt)
│   ├── 10.0.0.0/26 (Rack 1)
│   ├── 10.0.0.64/26 (Rack 2)
│   └── ...
├── 10.0.8.0/21 (VLAN 101 - oob)
├── 10.0.16.0/21 (VLAN 102 - bmc)
└── ...
```

### 5.3 Naming Conventions

```python
class NamingConventions:
    @staticmethod
    def tenant_name(region: str, number: int) -> str:
        return f"br-{region.lower()}-{number}"

    @staticmethod
    def facility_code(city: str, number: int) -> str:
        return f"{city.upper()}-DC-{number:02d}"

    @staticmethod
    def device_name(region: str, role: str, number: int) -> str:
        return f"{region.lower()}-{role}-srv-{number:02d}"
```

---

## 6. Data Flow - Site Allocation

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Frontend │    │ Backend  │    │ NetBox   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Fill form     │               │               │
     │ (region,      │               │               │
     │  base_prefix) │               │               │
     ├──────────────►│               │               │
     │               │ POST /api/v1/ │               │
     │               │ allocation/   │               │
     │               │ site          │               │
     │               ├──────────────►│               │
     │               │               │               │
     │               │               │ 1. Create     │
     │               │               │    Tenant     │
     │               │               ├──────────────►│
     │               │               │               │
     │               │               │ 2. Create     │
     │               │               │    Site       │
     │               │               ├──────────────►│
     │               │               │               │
     │               │               │ 3. Create     │
     │               │               │    VLANs (11) │
     │               │               ├──────────────►│
     │               │               │               │
     │               │               │ 4. Create     │
     │               │               │    Prefixes   │
     │               │               ├──────────────►│
     │               │               │               │
     │               │               │◄──────────────┤
     │               │◄──────────────┤               │
     │◄──────────────┤ Show results  │               │
     │               │               │               │
```

---

## 7. Data Flow - Device Sync

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  User    │    │ Frontend │    │ Backend  │    │ NetBox   │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     │ Click Sync    │               │               │
     ├──────────────►│               │               │
     │               │ GET /api/v1/  │               │
     │               │   devices/    │               │
     │               ├──────────────►│               │
     │               │               │ GET /dcim/    │
     │               │               │   devices/    │
     │               │               ├──────────────►│
     │               │               │               │
     │               │               │◄──────────────┤
     │               │               │  Device list  │
     │               │◄──────────────┤               │
     │◄──────────────┤ Display table │               │
     │               │ (read-only)   │               │
     │               │               │               │
     │ Click device  │               │               │
     │ name          │               │               │
     ├───────────────┼───────────────┼──────────────►│
     │               │               │  Open NetBox  │
     │               │               │  device page  │
```

---

## 8. Security Considerations

- **Authentication**: NetBox API token (planned: JWT)
- **Authorization**: Planned RBAC with roles (admin, operator, viewer)
- **API Security**: CORS configuration, input validation via Pydantic
- **Secrets**: Environment variables, never in code
- **Device Protection**: Read-only sync prevents accidental deletion

---

## 9. API Contract Examples

### Create Site Allocation

```http
POST /api/v1/allocation/site
Content-Type: application/json

{
  "region": "nordeste",
  "base_prefix": "10.1.0.0/16"
}
```

### Response

```json
{
  "tenant": {
    "id": 1,
    "name": "br-ne-1",
    "slug": "br-ne-1"
  },
  "site": {
    "id": 1,
    "name": "Site Nordeste",
    "slug": "site-nordeste",
    "facility": "NE-DC-01"
  },
  "vlans": [
    {"vid": 100, "name": "vlan-mgmt"},
    {"vid": 101, "name": "vlan-oob"},
    ...
  ],
  "prefixes": [
    {"prefix": "10.1.0.0/16", "status": "container"},
    {"prefix": "10.1.0.0/21", "vlan": 100},
    ...
  ]
}
```

### List Devices (Sync)

```http
GET /api/v1/devices/
```

### Response

```json
[
  {
    "id": 1,
    "name": "ne-db-srv-01",
    "device_type_name": "PowerEdge R750",
    "role_name": "Database Server",
    "site_name": "Site Nordeste",
    "status": "active",
    "serial": "DELL-NE-DB001"
  }
]
```

---

## 10. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Docker Compose                             │
│                                                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │    Frontend     │  │     Backend     │  │      NetBox         │  │
│  │   (Next.js)     │  │   (FastAPI)     │  │   (docker-compose   │  │
│  │   Port: 3000    │  │   Port: 8001    │  │    .netbox.yml)     │  │
│  └────────┬────────┘  └────────┬────────┘  │   Port: 8000        │  │
│           │                    │           └──────────┬──────────┘  │
│           │                    │                      │              │
│           └────────────────────┴──────────────────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

Services:
- Frontend: http://localhost:3000
- Backend:  http://localhost:8001
- NetBox:   http://localhost:8000
- API Docs: http://localhost:8001/docs
```

---

## 11. Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         IPAM PoC                             │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │  Prefixes   │    │   VLANs     │    │    Devices      │  │
│  │  (CRUD)     │    │   (CRUD)    │    │  (Read-Only)    │  │
│  └──────┬──────┘    └──────┬──────┘    └────────┬────────┘  │
│         │                  │                    │            │
│         └──────────────────┼────────────────────┘            │
│                            │                                 │
│  ┌─────────────┐    ┌──────┴──────┐    ┌─────────────────┐  │
│  │   Sites     │    │ Allocation  │    │    Tenants      │  │
│  │  (CRUD)     │    │  (Wizard)   │    │    (CRUD)       │  │
│  └──────┬──────┘    └──────┬──────┘    └────────┬────────┘  │
│         │                  │                    │            │
│         └──────────────────┼────────────────────┘            │
│                            │                                 │
│                     ┌──────┴──────┐                          │
│                     │   NetBox    │                          │
│                     │   Client    │                          │
│                     └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Approval

- [x] Tech Lead - Reinaldo Saraiva
- [ ] Security Review
- [ ] DevOps Review
