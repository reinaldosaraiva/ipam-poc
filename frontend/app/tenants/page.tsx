"use client";

import { useEffect, useState } from "react";
import { Users, Plus, Trash2 } from "lucide-react";
import { tenantApi, Tenant } from "@/lib/api";

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTenants = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await tenantApi.list({ limit: 100 });
      setTenants(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tenants");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTenants();
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this tenant?")) {
      try {
        await tenantApi.delete(id);
        loadTenants();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete tenant");
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tenants</h1>
          <p className="text-muted-foreground">
            Manage your organization tenants
          </p>
        </div>
        <a
          href="/allocation"
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add Tenant
        </a>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border bg-white p-8 text-center">
          <p className="text-muted-foreground">Loading tenants...</p>
        </div>
      ) : tenants.length === 0 ? (
        <div className="rounded-lg border bg-white p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <Users className="h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No tenants yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Use the Allocation page to create tenants with proper naming conventions.
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border bg-white">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Slug</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Description</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Tags</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {tenants.map((tenant) => (
                <tr key={tenant.id} className="border-b last:border-0">
                  <td className="px-4 py-3 font-medium">{tenant.name}</td>
                  <td className="px-4 py-3 font-mono text-sm text-muted-foreground">
                    {tenant.slug}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {tenant.description || "-"}
                  </td>
                  <td className="px-4 py-3">
                    {tenant.tags.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {tenant.tags.map((tag) => (
                          <span
                            key={tag}
                            className="inline-flex rounded-full bg-muted px-2 py-0.5 text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(tenant.id)}
                      className="inline-flex items-center justify-center rounded p-1 text-red-600 hover:bg-red-50"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
