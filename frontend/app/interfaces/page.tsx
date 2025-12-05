"use client";

import { Cable, Plus } from "lucide-react";

export default function InterfacesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Interfaces</h1>
          <p className="text-muted-foreground">
            Manage network interfaces and connections
          </p>
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90">
          <Plus className="h-4 w-4" />
          Add Interface
        </button>
      </div>

      <div className="rounded-lg border bg-white p-8">
        <div className="flex flex-col items-center justify-center text-center">
          <Cable className="h-12 w-12 text-muted-foreground/50" />
          <h3 className="mt-4 text-lg font-semibold">No interfaces yet</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Interfaces will appear here once devices are configured.
          </p>
        </div>
      </div>
    </div>
  );
}
