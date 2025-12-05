"use client";

import { Trash2, Edit, ExternalLink } from "lucide-react";
import { Prefix } from "@/lib/api";

interface PrefixTableProps {
  prefixes: Prefix[];
  onDelete: (id: number) => void;
  onRefresh: () => void;
}

const statusColors: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  reserved: "bg-yellow-100 text-yellow-800",
  deprecated: "bg-red-100 text-red-800",
  container: "bg-blue-100 text-blue-800",
};

export function PrefixTable({ prefixes, onDelete, onRefresh }: PrefixTableProps) {
  if (prefixes.length === 0) {
    return (
      <div className="rounded-lg border bg-white p-8 text-center">
        <p className="text-muted-foreground">No prefixes found.</p>
        <p className="text-sm text-muted-foreground mt-1">
          Create your first prefix to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-white overflow-hidden">
      <table className="w-full">
        <thead className="bg-muted/50">
          <tr>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Prefix
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Status
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Site
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Tenant
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Description
            </th>
            <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">
              Pool
            </th>
            <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {prefixes.map((prefix) => (
            <tr key={prefix.id} className="hover:bg-muted/30">
              <td className="px-4 py-3">
                <code className="rounded bg-muted px-2 py-1 text-sm font-mono">
                  {prefix.prefix}
                </code>
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                    statusColors[prefix.status] || "bg-gray-100"
                  }`}
                >
                  {prefix.status}
                </span>
              </td>
              <td className="px-4 py-3 text-sm">
                {prefix.site?.name || "-"}
              </td>
              <td className="px-4 py-3 text-sm">
                {prefix.tenant?.name || "-"}
              </td>
              <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate">
                {prefix.description || "-"}
              </td>
              <td className="px-4 py-3 text-sm">
                {prefix.is_pool ? (
                  <span className="text-green-600">Yes</span>
                ) : (
                  <span className="text-muted-foreground">No</span>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex justify-end gap-2">
                  <button
                    className="rounded p-1 hover:bg-muted"
                    title="View details"
                  >
                    <ExternalLink className="h-4 w-4 text-muted-foreground" />
                  </button>
                  <button
                    className="rounded p-1 hover:bg-muted"
                    title="Edit"
                  >
                    <Edit className="h-4 w-4 text-muted-foreground" />
                  </button>
                  <button
                    onClick={() => onDelete(prefix.id)}
                    className="rounded p-1 hover:bg-red-100"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
