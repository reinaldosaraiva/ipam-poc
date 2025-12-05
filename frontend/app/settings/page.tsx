"use client";

import { Settings, Save } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Configure your IPAM application
        </p>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <h2 className="text-lg font-semibold mb-4">NetBox Connection</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">
              NetBox URL
            </label>
            <input
              type="text"
              defaultValue="http://localhost:8000"
              className="w-full max-w-md rounded-lg border px-3 py-2 text-sm"
              disabled
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Configured via environment variable
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              API Token
            </label>
            <input
              type="password"
              defaultValue="••••••••••••••••••••"
              className="w-full max-w-md rounded-lg border px-3 py-2 text-sm"
              disabled
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Configured via environment variable
            </p>
          </div>

          <div className="flex items-center gap-2 pt-4">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-green-600">Connected to NetBox</span>
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <h2 className="text-lg font-semibold mb-4">Application Info</h2>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between max-w-md">
            <span className="text-muted-foreground">Version</span>
            <span>0.1.0</span>
          </div>
          <div className="flex justify-between max-w-md">
            <span className="text-muted-foreground">Frontend</span>
            <span>Next.js 14</span>
          </div>
          <div className="flex justify-between max-w-md">
            <span className="text-muted-foreground">Backend</span>
            <span>FastAPI</span>
          </div>
        </div>
      </div>
    </div>
  );
}
