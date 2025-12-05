# IPAM Web Application - Product Requirements Document

> **Version:** 2.0
> **Date:** 2025-12-05
> **Status:** Implemented

## Overview

Web application for IP Address Management migrated from Terraform-based NetBox automation.
Implements naming conventions and allocation patterns from [net-automation](https://github.com/phenriiique/net-automation).

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | Next.js 14 (React/TypeScript) |
| Database | PostgreSQL (via NetBox) |
| Integration | NetBox API (pynetbox) |

---

## 1. Functional Requirements

### 1.1 IP Prefix Management (IPAM Core)

- **CRUD Operations**: Create, read, update, delete IP prefixes/subnets
- **Attributes**: prefix, status, site_id, tenant_id, vlan_id, is_pool, role_id, tags
- **Status Values**: active, reserved, deprecated, container
- **Hierarchical Allocation**:
  - Container prefix: /16 per site
  - VLAN subnets: /21 per VLAN category
  - Host subnets: /26 per rack

### 1.2 VLAN Management

- **CRUD Operations**: Manage VLANs with full lifecycle
- **Attributes**: name, vid (1-4094), status, site_id, tenant_id, group_id, tags
- **Predefined Allocation Ranges**:
  - Management VLANs: 100-199
  - Data VLANs: 250-299

### 1.3 Device Inventory

- **Sync-Only Mode**: Devices are read-only, synced from NetBox
- **No CRUD**: Cannot create or delete devices from IPAM
- **Attributes Displayed**: name, serial, device_type, site, role, status
- **NetBox Link**: Direct link to manage device in NetBox

### 1.4 Site Management

- **CRUD Operations**: Create, read, update, delete sites
- **Attributes**: name, slug, status, description, tenant_id
- **Naming Convention**: Auto-generated slug from name
- **Facility Code**: Format `{CITY}-DC-{NUMBER}` (e.g., NE-DC-01)

### 1.5 Tenant Management

- **CRUD Operations**: Create, read, update, delete tenants
- **Attributes**: name, slug, description, tags
- **Naming Convention**: Format `br-{region}-{number}` (e.g., br-ne-1)

### 1.6 Site Allocation (Automated Provisioning)

Complete site provisioning in a single operation:

1. **Create Tenant** with naming convention
2. **Create Site** with facility code
3. **Create VLANs** (predefined management + data VLANs)
4. **Create Prefixes** (hierarchical allocation)

**Predefined VLANs:**

| VID | Name | Category |
|-----|------|----------|
| 100 | vlan-mgmt | Management |
| 101 | vlan-oob | Management |
| 102 | vlan-bmc | Management |
| 103 | vlan-pxe | Management |
| 250 | vlan-k8s-nodes | Data |
| 251 | vlan-k8s-pods | Data |
| 252 | vlan-k8s-svc | Data |
| 253 | vlan-storage | Data |
| 254 | vlan-backup | Data |
| 255 | vlan-replication | Data |
| 256 | vlan-external | Data |

### 1.7 Naming Conventions

- **Slug Generation**: Auto-generate from name with Portuguese accent support
- **Site Names**: `Site {Region}` → slug `site-{region}`
- **Tenant Names**: `br-{region}-{number}`
- **VLAN Names**: `vlan-{purpose}` (e.g., vlan-mgmt, vlan-k8s-nodes)
- **Device Names**: `{region}-{role}-srv-{number}` (e.g., ne-db-srv-01)

### 1.8 Interface Configuration (Future)

- **CRUD Operations**: Configure network interfaces
- **Attributes**: name, device_id, type, mode, tagged_vlans, untagged_vlan

### 1.9 Bulk Operations (Future)

- Bulk creation via CSV/JSON import
- Bulk update of multiple records
- Bulk delete with confirmation

### 1.10 Search and Filtering

- Full-text search across all entities
- Filter by site, tenant, status, tags
- Advanced query builder

---

## 2. Non-Functional Requirements

| Requirement | Target | Status |
|-------------|--------|--------|
| Response Time | < 500ms for CRUD operations | Implemented |
| Authentication | OAuth2 / JWT | Planned |
| Authorization | RBAC (Role-Based Access Control) | Planned |
| Scalability | 10,000 devices, 100,000 prefixes | Designed |
| Availability | 99.9% uptime | Designed |

---

## 3. User Stories

| ID | Role | Story | Priority | Status |
|----|------|-------|----------|--------|
| US-01 | Network Admin | Manage IP prefixes and VLANs efficiently | High | Done |
| US-02 | Network Admin | Allocate complete site infrastructure in one operation | High | Done |
| US-03 | System Admin | View device inventory synced from NetBox | High | Done |
| US-04 | Network Engineer | Follow naming conventions automatically | High | Done |
| US-05 | Tenant Manager | Assign resources to tenants | Medium | Done |
| US-06 | Operator | View dashboard with network overview | Medium | Partial |
| US-07 | Security Officer | Secure access with RBAC | High | Planned |
| US-08 | System Admin | Perform bulk operations on devices | Medium | Planned |
| US-09 | Auditor | Access audit logs of changes | Low | Planned |

---

## 4. API Endpoints

```
/api/v1/
├── prefixes/              # IP Prefix CRUD
├── vlans/                 # VLAN CRUD
├── devices/               # Device READ-ONLY (sync from NetBox)
├── sites/                 # Site CRUD
├── tenants/               # Tenant CRUD
├── interfaces/            # Interface CRUD (planned)
├── allocation/            # Automated allocation
│   ├── vlan-definitions/  # Predefined VLANs
│   ├── vlan-ranges/       # VLAN range rules
│   ├── naming/preview/    # Preview naming
│   ├── plan/              # Plan allocation
│   ├── execute/           # Execute allocation
│   └── site/              # Complete site allocation
├── bulk/                  # Bulk operations (planned)
│   ├── import/
│   └── export/
└── auth/                  # Authentication (planned)
    ├── login/
    └── refresh/
```

---

## 5. Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Time to provision site | < 30 seconds (vs 2-5 min with Terraform) | Achieved |
| API response time | < 500ms | Achieved |
| Error rate | < 1% for API operations | Achieved |
| User adoption | 80% of network team within 1 month | Pending |
| User satisfaction | NPS > 40 | Pending |

---

## 6. Out of Scope (v1.0)

- Cable management
- Rack visualization
- Circuit provisioning
- Automated IP discovery
- Full authentication (using NetBox token for now)

---

## 7. Example Data (Demo)

### Sites

| Name | Slug | Tenant |
|------|------|--------|
| Site Nordeste | site-nordeste | br-ne-1 |
| Site Sudeste | site-sudeste | br-se-1 |

### Devices

| Device | Type | Site | Role |
|--------|------|------|------|
| ne-db-srv-01 | Dell PowerEdge R750 | Nordeste | Database Server |
| ne-db-srv-02 | Lenovo ThinkSystem SR650 | Nordeste | Database Server |
| ne-app-srv-01 | Dell PowerEdge R650 | Nordeste | Application Server |
| ne-app-srv-02 | Lenovo ThinkSystem SR630 | Nordeste | Application Server |
| se-db-srv-01 | Dell PowerEdge R750 | Sudeste | Database Server |
| se-db-srv-02 | Lenovo ThinkSystem SR650 | Sudeste | Database Server |
| se-app-srv-01 | Dell PowerEdge R650 | Sudeste | Application Server |
| se-app-srv-02 | Lenovo ThinkSystem SR630 | Sudeste | Application Server |

---

## Approval

- [x] Product Owner - Reinaldo Saraiva
- [x] Tech Lead - Reinaldo Saraiva
- [ ] Security Review
