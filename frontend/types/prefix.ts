/**
 * Prefix type definitions
 */

export type PrefixStatus = "active" | "reserved" | "deprecated" | "container";

export interface NestedSite {
  id: number;
  name: string;
}

export interface NestedTenant {
  id: number;
  name: string;
}

export interface Prefix {
  id: number;
  prefix: string;
  status: PrefixStatus;
  description: string | null;
  site_id: number | null;
  tenant_id: number | null;
  vlan_id: number | null;
  role_id: number | null;
  is_pool: boolean;
  tags: string[];
  site: NestedSite | null;
  tenant: NestedTenant | null;
  created: string;
  last_updated: string;
}

export interface PrefixCreate {
  prefix: string;
  status?: PrefixStatus;
  description?: string;
  site_id?: number;
  tenant_id?: number;
  vlan_id?: number;
  role_id?: number;
  is_pool?: boolean;
  tags?: string[];
}

export interface PrefixUpdate {
  status?: PrefixStatus;
  description?: string;
  site_id?: number;
  tenant_id?: number;
  vlan_id?: number;
  role_id?: number;
  is_pool?: boolean;
  tags?: string[];
}
