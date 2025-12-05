"use client";

import { useEffect, useState } from "react";
import { Layers, Plus, Trash2, X } from "lucide-react";
import { vlanApi, Vlan } from "@/lib/api";

export default function VlansPage() {
  const [vlans, setVlans] = useState<Vlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    vid: 100,
    status: "active",
    description: "",
  });

  const loadVlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await vlanApi.list({ limit: 100 });
      setVlans(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load VLANs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadVlans();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      const response = await fetch("http://localhost:8001/api/v1/vlans/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Failed to create VLAN");
      }
      setIsCreateOpen(false);
      setFormData({ name: "", vid: 100, status: "active", description: "" });
      loadVlans();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create VLAN");
    }
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this VLAN?")) {
      try {
        const response = await fetch(`http://localhost:8001/api/v1/vlans/${id}`, {
          method: "DELETE",
        });
        if (!response.ok) {
          throw new Error("Failed to delete VLAN");
        }
        loadVlans();
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete VLAN");
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-700";
      case "reserved":
        return "bg-yellow-100 text-yellow-700";
      case "deprecated":
        return "bg-red-100 text-red-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">VLANs</h1>
          <p className="text-muted-foreground">
            Manage your VLANs and network segmentation
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add VLAN
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-lg bg-white p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Create VLAN</h2>
              <button onClick={() => setIsCreateOpen(false)}>
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                  placeholder="VLAN 100 - Management"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">VLAN ID</label>
                <input
                  type="number"
                  value={formData.vid}
                  onChange={(e) => setFormData({ ...formData, vid: parseInt(e.target.value) })}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                  min={1}
                  max={4094}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                >
                  <option value="active">Active</option>
                  <option value="reserved">Reserved</option>
                  <option value="deprecated">Deprecated</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                  placeholder="Management network"
                />
              </div>
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsCreateOpen(false)}
                  className="flex-1 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border bg-white p-8 text-center">
          <p className="text-muted-foreground">Loading VLANs...</p>
        </div>
      ) : vlans.length === 0 ? (
        <div className="rounded-lg border bg-white p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <Layers className="h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No VLANs yet</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Click "Add VLAN" to create your first VLAN or use the Allocation page.
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border bg-white">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-sm font-medium">VID</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Description</th>
                <th className="px-4 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {vlans.map((vlan) => (
                <tr key={vlan.id} className="border-b last:border-0">
                  <td className="px-4 py-3 font-mono font-medium">{vlan.vid}</td>
                  <td className="px-4 py-3">{vlan.name}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(vlan.status)}`}>
                      {vlan.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {vlan.description || "-"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleDelete(vlan.id)}
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
