"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { PrefixCreate } from "@/lib/api";

interface PrefixFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: PrefixCreate) => Promise<void>;
}

export function PrefixFormDialog({
  open,
  onOpenChange,
  onSubmit,
}: PrefixFormDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const data: PrefixCreate = {
      prefix: formData.get("prefix") as string,
      status: (formData.get("status") as string) || "active",
      description: (formData.get("description") as string) || undefined,
      is_pool: formData.get("is_pool") === "on",
    };

    try {
      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create prefix");
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Create IP Prefix</h2>
          <button
            onClick={() => onOpenChange(false)}
            className="rounded p-1 hover:bg-muted"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              Prefix (CIDR) *
            </label>
            <input
              type="text"
              name="prefix"
              placeholder="10.0.0.0/24"
              required
              pattern="^([0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]{1,2}$"
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Enter a valid CIDR notation (e.g., 192.168.1.0/24)
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <select
              name="status"
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="active">Active</option>
              <option value="reserved">Reserved</option>
              <option value="deprecated">Deprecated</option>
              <option value="container">Container</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              Description
            </label>
            <textarea
              name="description"
              rows={2}
              placeholder="Optional description..."
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              name="is_pool"
              id="is_pool"
              className="rounded border-gray-300"
            />
            <label htmlFor="is_pool" className="text-sm">
              Is Pool (allow automatic IP assignment)
            </label>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => onOpenChange(false)}
              className="flex-1 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50"
            >
              {loading ? "Creating..." : "Create Prefix"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
