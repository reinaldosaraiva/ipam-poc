# IPAM PoC - IP Address Management

Web application for managing IP addresses, VLANs, and network devices.
Integrates with NetBox as the source of truth, following naming conventions from [net-automation](https://github.com/phenriiique/net-automation).

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI + Python 3.11 + Pydantic v2 |
| **Frontend** | Next.js 14 + TypeScript + TailwindCSS |
| **Integration** | NetBox REST API (pynetbox) |
| **Infrastructure** | Docker Compose |

## Features

### Implemented

- [x] **IP Prefix Management** - Full CRUD with hierarchical allocation
- [x] **VLAN Management** - Full CRUD with predefined allocation patterns
- [x] **Site Management** - Full CRUD with tenant association
- [x] **Tenant Management** - Full CRUD
- [x] **Device Inventory** - Read-only sync from NetBox
- [x] **Site Allocation** - Automated provisioning (tenant + site + VLANs + prefixes)
- [x] **Naming Conventions** - Auto-generated slugs with Portuguese accent support
- [x] **Allocation Rules** - VLAN ranges and hierarchical prefix allocation

### Allocation Patterns

| Category | VLAN Range | Prefixes |
|----------|------------|----------|
| Management | 100-199 | /21 per VLAN |
| Data | 250-299 | /21 per VLAN |
| Host Subnets | - | /26 per rack |

**Predefined VLANs:**

| VID | Name | Purpose |
|-----|------|---------|
| 100 | vlan-mgmt | Management |
| 101 | vlan-oob | Out-of-band |
| 102 | vlan-bmc | BMC/IPMI |
| 103 | vlan-pxe | PXE Boot |
| 250 | vlan-k8s-nodes | Kubernetes nodes |
| 251 | vlan-k8s-pods | Kubernetes pods |
| 252 | vlan-k8s-svc | Kubernetes services |
| 253 | vlan-storage | Storage network |
| 254 | vlan-backup | Backup network |
| 255 | vlan-replication | Replication |
| 256 | vlan-external | External access |

## Project Structure

```
ipam-poc/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/v1/         # REST API routers
│   │   │   ├── prefixes.py
│   │   │   ├── vlans.py
│   │   │   ├── devices.py
│   │   │   ├── sites.py
│   │   │   ├── tenants.py
│   │   │   └── allocation.py
│   │   ├── domain/         # Business logic
│   │   │   └── allocation/
│   │   │       ├── naming.py    # Naming conventions
│   │   │       └── rules.py     # Allocation rules
│   │   ├── infrastructure/ # NetBox client
│   │   ├── schemas/        # Pydantic models
│   │   └── utils/          # Utilities
│   │       └── slug.py     # Slug generation
│   └── tests/              # Pytest tests
├── frontend/               # Next.js Frontend
│   ├── app/                # App Router pages
│   │   ├── prefixes/
│   │   ├── vlans/
│   │   ├── devices/
│   │   ├── sites/
│   │   ├── tenants/
│   │   └── allocation/
│   ├── components/         # React components
│   └── lib/                # API client
└── docs/                   # Documentation
    ├── PRD.md              # Product Requirements
    └── HLD.md              # High-Level Design
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- NetBox instance (included in docker-compose.netbox.yml)

### Running with Docker Compose

```bash
# Start NetBox (if needed)
docker compose -f docker-compose.netbox.yml up -d

# Start IPAM application
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8001 | - |
| NetBox | http://localhost:8000 | admin / admin |
| API Docs | http://localhost:8001/docs | - |

### Development Setup

**Backend:**

```bash
cd backend
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8001
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Core Resources

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/v1/prefixes/` | List/Create IP prefixes |
| GET/PATCH/DELETE | `/api/v1/prefixes/{id}` | Get/Update/Delete prefix |
| GET/POST | `/api/v1/vlans/` | List/Create VLANs |
| GET/PATCH/DELETE | `/api/v1/vlans/{id}` | Get/Update/Delete VLAN |
| GET | `/api/v1/devices/` | List devices (sync from NetBox) |
| GET/POST | `/api/v1/sites/` | List/Create sites |
| GET/PATCH/DELETE | `/api/v1/sites/{id}` | Get/Update/Delete site |
| GET/POST | `/api/v1/tenants/` | List/Create tenants |
| GET/PATCH/DELETE | `/api/v1/tenants/{id}` | Get/Update/Delete tenant |

### Allocation API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/allocation/vlan-definitions` | List predefined VLANs |
| GET | `/api/v1/allocation/vlan-ranges` | Get VLAN range rules |
| POST | `/api/v1/allocation/naming/preview` | Preview naming conventions |
| POST | `/api/v1/allocation/plan` | Plan site allocation |
| POST | `/api/v1/allocation/execute` | Execute site allocation |
| POST | `/api/v1/allocation/site` | Complete site allocation |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | OpenAPI documentation |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETBOX_URL` | NetBox API URL | `http://localhost:8000` |
| `NETBOX_TOKEN` | NetBox API token | (required) |
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["http://localhost:3000"]` |

## Running Tests

```bash
cd backend
uv run pytest
uv run pytest --cov=app --cov-report=html
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │───▶│     Backend     │───▶│     NetBox      │
│   (Next.js)     │    │   (FastAPI)     │    │   (REST API)    │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                      │
        │              ┌───────┴───────┐
        │              │  Allocation   │
        │              │   Service     │
        │              └───────────────┘
        │                      │
        └──────────────────────┘
                    │
            ┌───────┴───────┐
            │    Naming     │
            │  Conventions  │
            └───────────────┘
```

## Device Sync Mode

Devices are **read-only** - they can only be synced from NetBox, not created or deleted from IPAM.
This ensures NetBox remains the authoritative source for device inventory.

To manage devices:
1. Create/edit devices in NetBox: http://localhost:8000/dcim/devices/
2. Click "Sync" in IPAM frontend to refresh the list

## License

MIT
