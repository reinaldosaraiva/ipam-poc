# IPAM Web Application - Product Requirements Document

> **Version:** 2.1
> **Date:** 2025-12-05
> **Status:** Implemented
> **Reference:** [net-automation](https://github.com/phenriiique/net-automation)

## Overview

Web application for IP Address Management migrated from Terraform-based NetBox automation.
Implements naming conventions and allocation patterns from the net-automation project.

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11+) |
| Frontend | Next.js 14 (React/TypeScript) |
| Database | PostgreSQL (via NetBox) |
| Integration | NetBox API (pynetbox) |

---

## 1. Architecture Diagrams

### 1.1 System Context (C4)

![C4 Context](diagrams/c4-context.png)

### 1.2 Container Diagram (C4)

![C4 Container](diagrams/c4-container.png)

### 1.3 Site Allocation Flow

![Sequence Allocation](diagrams/sequence-allocation.png)

### 1.4 Device Sync Flow

![Sequence Device Sync](diagrams/sequence-device-sync.png)

---

## 2. Naming Conventions (Regras de Nomenclatura)

### 2.1 Tenant Naming

| Pattern | Format | Example |
|---------|--------|---------|
| Tenant Name | `br-{region}-{number}` | `br-ne-1`, `br-se-2` |
| Tenant Slug | Same as name | `br-ne-1` |

**Region Codes:**

| Region | Code | Description |
|--------|------|-------------|
| Nordeste | `ne` | Northeast Brazil |
| Sudeste | `se` | Southeast Brazil |
| Sul | `su` | South Brazil |
| Centro-Oeste | `co` | Central-West Brazil |
| Norte | `no` | North Brazil |

### 2.2 Site Naming

| Pattern | Format | Example |
|---------|--------|---------|
| Site Name | `Site {Region}` | `Site Nordeste` |
| Site Slug | `site-{region}` | `site-nordeste` |
| Facility Code | `{REGION}-DC-{NUMBER}` | `NE-DC-01` |

**Slug Generation Rules:**
- Convert to lowercase
- Replace spaces with hyphens
- Remove Portuguese accents (é→e, ã→a, ç→c)
- Remove special characters
- Collapse multiple hyphens

```python
# Example: "São Paulo" → "sao-paulo"
# Example: "Região Nordeste" → "regiao-nordeste"
```

### 2.3 VLAN Naming

| Pattern | Format | Example |
|---------|--------|---------|
| VLAN Name | `vlan-{purpose}` | `vlan-mgmt`, `vlan-k8s-nodes` |
| VLAN Description | `{Purpose} network` | `Management network` |

### 2.4 Device Naming

| Pattern | Format | Example |
|---------|--------|---------|
| Database Server | `{region}-db-srv-{number}` | `ne-db-srv-01` |
| Application Server | `{region}-app-srv-{number}` | `ne-app-srv-02` |
| Generic Server | `{region}-srv-{number}` | `se-srv-01` |

### 2.5 Rack Naming

| Pattern | Format | Example |
|---------|--------|---------|
| Rack Name | `{site}-rack-{number}` | `ne-rack-01` |

---

## 3. Allocation Rules (Regras de Alocação)

### 3.1 VLAN Allocation Ranges

| Category | VID Range | Purpose |
|----------|-----------|---------|
| **Management** | 100-199 | Infrastructure, OOB, BMC, PXE |
| **Data** | 250-299 | Applications, storage, services |
| **User** | 300-399 | End-user networks (future) |
| **Guest** | 400-499 | Guest/visitor networks (future) |

### 3.2 Predefined VLANs

#### Management VLANs (100-199)

| VID | Name | Description | Use Case |
|-----|------|-------------|----------|
| 100 | `vlan-mgmt` | Management | SSH, SNMP, monitoring |
| 101 | `vlan-oob` | Out-of-band | Console servers, KVM |
| 102 | `vlan-bmc` | BMC/IPMI | Server management (iDRAC, iLO) |
| 103 | `vlan-pxe` | PXE Boot | OS deployment, imaging |

#### Data VLANs (250-299)

| VID | Name | Description | Use Case |
|-----|------|-------------|----------|
| 250 | `vlan-k8s-nodes` | Kubernetes nodes | K8s node communication |
| 251 | `vlan-k8s-pods` | Kubernetes pods | Pod network (CNI) |
| 252 | `vlan-k8s-svc` | Kubernetes services | Service mesh, ingress |
| 253 | `vlan-storage` | Storage network | iSCSI, NFS, Ceph |
| 254 | `vlan-backup` | Backup network | Backup traffic isolation |
| 255 | `vlan-replication` | Replication | DR, database replication |
| 256 | `vlan-external` | External access | DMZ, public services |

### 3.3 IP Prefix Allocation Hierarchy

```
Site Container (/16)
├── VLAN Subnets (/21) - 2,048 hosts each
│   └── Host Subnets (/26) - 62 hosts each (per rack)
```

#### Prefix Size Rules

| Level | CIDR | Hosts | Purpose |
|-------|------|-------|---------|
| Container | /16 | 65,534 | Site-level aggregate |
| VLAN Subnet | /21 | 2,046 | Per-VLAN allocation |
| Host Subnet | /26 | 62 | Per-rack allocation |

#### Allocation Example

For base prefix `10.1.0.0/16` (Site Nordeste):

```
10.1.0.0/16 (Container - Site Nordeste)
├── 10.1.0.0/21   (VLAN 100 - vlan-mgmt)
│   ├── 10.1.0.0/26   (Rack 1)
│   ├── 10.1.0.64/26  (Rack 2)
│   ├── 10.1.0.128/26 (Rack 3)
│   └── ...
├── 10.1.8.0/21   (VLAN 101 - vlan-oob)
├── 10.1.16.0/21  (VLAN 102 - vlan-bmc)
├── 10.1.24.0/21  (VLAN 103 - vlan-pxe)
├── 10.1.32.0/21  (VLAN 250 - vlan-k8s-nodes)
├── 10.1.40.0/21  (VLAN 251 - vlan-k8s-pods)
├── 10.1.48.0/21  (VLAN 252 - vlan-k8s-svc)
├── 10.1.56.0/21  (VLAN 253 - vlan-storage)
├── 10.1.64.0/21  (VLAN 254 - vlan-backup)
├── 10.1.72.0/21  (VLAN 255 - vlan-replication)
└── 10.1.80.0/21  (VLAN 256 - vlan-external)
```

### 3.4 Prefix Status Rules

| Status | Use Case |
|--------|----------|
| `container` | Aggregate prefixes (site-level /16) |
| `active` | In-use subnets |
| `reserved` | Planned but not deployed |
| `deprecated` | Being phased out |

---

## 4. Functional Requirements

### 4.1 IP Prefix Management (IPAM Core)

- **CRUD Operations**: Create, read, update, delete IP prefixes/subnets
- **Attributes**: prefix, status, site_id, tenant_id, vlan_id, is_pool, role_id, tags
- **Status Values**: active, reserved, deprecated, container
- **Hierarchical Allocation**: Automatic subnet calculation based on rules

### 4.2 VLAN Management

- **CRUD Operations**: Manage VLANs with full lifecycle
- **Attributes**: name, vid (1-4094), status, site_id, tenant_id, group_id, tags
- **Predefined Templates**: 11 VLANs auto-created per site

### 4.3 Device Inventory

- **Sync-Only Mode**: Devices are read-only, synced from NetBox
- **No CRUD from IPAM**: Cannot create or delete devices
- **NetBox Link**: Direct link to manage device in NetBox
- **Rationale**: NetBox is the authoritative source for device inventory

### 4.4 Site Management

- **CRUD Operations**: Create, read, update, delete sites
- **Auto-generation**: Slug and facility code generated from name
- **Tenant Association**: Each site belongs to a tenant

### 4.5 Tenant Management

- **CRUD Operations**: Create, read, update, delete tenants
- **Naming Convention**: Follows `br-{region}-{number}` pattern

### 4.6 Site Allocation (Automated Provisioning)

Complete site provisioning in a single operation:

1. **Create Tenant** with naming convention
2. **Create Site** with facility code
3. **Create VLANs** (11 predefined)
4. **Create Prefixes** (container + 11 VLAN subnets)

---

## 5. Non-Functional Requirements

| Requirement | Target | Status |
|-------------|--------|--------|
| Response Time | < 500ms for CRUD operations | Implemented |
| Allocation Time | < 30 seconds for full site | Implemented |
| Authentication | OAuth2 / JWT | Planned |
| Authorization | RBAC (admin, operator, viewer) | Planned |
| Scalability | 10,000 devices, 100,000 prefixes | Designed |

---

## 6. User Stories

| ID | Role | Story | Priority | Status |
|----|------|-------|----------|--------|
| US-01 | Network Admin | Manage IP prefixes following allocation rules | High | Done |
| US-02 | Network Admin | Allocate complete site with one click | High | Done |
| US-03 | Network Admin | VLANs auto-created with naming conventions | High | Done |
| US-04 | System Admin | View device inventory synced from NetBox | High | Done |
| US-05 | Network Engineer | Slugs auto-generated with Portuguese support | High | Done |
| US-06 | Tenant Manager | Assign resources to tenants | Medium | Done |
| US-07 | Security Officer | Secure access with RBAC | High | Planned |

---

## 7. API Endpoints

```
/api/v1/
├── prefixes/              # IP Prefix CRUD
├── vlans/                 # VLAN CRUD
├── devices/               # Device READ-ONLY (sync from NetBox)
├── sites/                 # Site CRUD
├── tenants/               # Tenant CRUD
├── allocation/            # Automated allocation
│   ├── vlan-definitions/  # GET predefined VLANs
│   ├── vlan-ranges/       # GET VLAN range rules
│   ├── naming/preview/    # POST preview naming
│   ├── plan/              # POST plan allocation
│   ├── execute/           # POST execute plan
│   └── site/              # POST complete site allocation
```

---

## 8. Example Data

### Sites Allocated

| Site | Tenant | Base Prefix | VLANs | Status |
|------|--------|-------------|-------|--------|
| Site Nordeste | br-ne-1 | 10.1.0.0/16 | 100-103, 250-256 | Active |
| Site Sudeste | br-se-1 | 10.2.0.0/16 | 100-103, 250-256 | Active |

### Devices (Synced from NetBox)

| Device | Manufacturer | Model | Site | Role |
|--------|--------------|-------|------|------|
| ne-db-srv-01 | Dell | PowerEdge R750 | Nordeste | Database Server |
| ne-db-srv-02 | Lenovo | ThinkSystem SR650 | Nordeste | Database Server |
| ne-app-srv-01 | Dell | PowerEdge R650 | Nordeste | Application Server |
| ne-app-srv-02 | Lenovo | ThinkSystem SR630 | Nordeste | Application Server |
| se-db-srv-01 | Dell | PowerEdge R750 | Sudeste | Database Server |
| se-db-srv-02 | Lenovo | ThinkSystem SR650 | Sudeste | Database Server |
| se-app-srv-01 | Dell | PowerEdge R650 | Sudeste | Application Server |
| se-app-srv-02 | Lenovo | ThinkSystem SR630 | Sudeste | Application Server |

---

## 9. Out of Scope (v1.0)

- Cable management
- Rack visualization
- Circuit provisioning
- Automated IP discovery
- Full authentication (using NetBox token)

---

## Approval

- [x] Product Owner - Reinaldo Saraiva
- [x] Tech Lead - Reinaldo Saraiva
- [ ] Security Review
