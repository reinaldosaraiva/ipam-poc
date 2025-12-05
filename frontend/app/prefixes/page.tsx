"use client";

import { useEffect, useState } from "react";
import { Plus, Search, Filter } from "lucide-react";
import { prefixApi, Prefix } from "@/lib/api";
import { PrefixTable } from "@/components/features/prefix-table";
import { PrefixFormDialog } from "@/components/features/prefix-form";

export default function PrefixesPage() {
  const [prefixes, setPrefixes] = useState<Prefix[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  const loadPrefixes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await prefixApi.list({ limit: 100 });
      setPrefixes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load prefixes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPrefixes();
  }, []);

  const filteredPrefixes = prefixes.filter(
    (p) =>
      p.prefix.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCreate = async (data: any) => {
    await prefixApi.create(data);
    setIsCreateOpen(false);
    loadPrefixes();
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this prefix?")) {
      await prefixApi.delete(id);
      loadPrefixes();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">IP Prefixes</h1>
          <p className="text-muted-foreground">
            Manage your network prefixes and subnets
          </p>
        </div>
        <button
          onClick={() => setIsCreateOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          Add Prefix
        </button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search prefixes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border bg-white py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border bg-white px-4 py-2 text-sm font-medium hover:bg-muted">
          <Filter className="h-4 w-4" />
          Filters
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border bg-white p-8 text-center">
          <p className="text-muted-foreground">Loading prefixes...</p>
        </div>
      ) : (
        <PrefixTable
          prefixes={filteredPrefixes}
          onDelete={handleDelete}
          onRefresh={loadPrefixes}
        />
      )}

      <PrefixFormDialog
        open={isCreateOpen}
        onOpenChange={setIsCreateOpen}
        onSubmit={handleCreate}
      />
    </div>
  );
}
