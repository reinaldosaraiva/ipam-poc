"use client";

import { useEffect, useState } from "react";
import { Server, RefreshCw, ExternalLink } from "lucide-react";
import { deviceApi, Device } from "@/lib/api";

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await deviceApi.list({ limit: 100 });
      setDevices(data);
      setLastSync(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load devices");
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    await loadDevices();
    setSyncing(false);
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-700";
      case "planned":
        return "bg-blue-100 text-blue-700";
      case "staged":
        return "bg-yellow-100 text-yellow-700";
      case "failed":
        return "bg-red-100 text-red-700";
      case "offline":
        return "bg-gray-100 text-gray-700";
      default:
        return "bg-gray-100 text-gray-700";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Devices</h1>
          <p className="text-muted-foreground">
            Synchronized from NetBox (read-only)
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleSync}
            disabled={syncing}
            className="inline-flex items-center gap-2 rounded-lg border bg-white px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${syncing ? "animate-spin" : ""}`} />
            Sync
          </button>
          <a
            href="http://localhost:8000/dcim/devices/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90"
          >
            <ExternalLink className="h-4 w-4" />
            Manage in NetBox
          </a>
        </div>
      </div>

      <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700 flex items-center justify-between">
        <span>
          <strong>Sync Mode:</strong> Devices are read-only. Manage devices directly in NetBox.
        </span>
        {lastSync && (
          <span className="text-xs">
            Last sync: {lastSync.toLocaleTimeString()}
          </span>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="rounded-lg border bg-white p-8 text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
          <p className="mt-2 text-muted-foreground">Syncing with NetBox...</p>
        </div>
      ) : devices.length === 0 ? (
        <div className="rounded-lg border bg-white p-8">
          <div className="flex flex-col items-center justify-center text-center">
            <Server className="h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold">No devices in NetBox</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Add devices in NetBox and click Sync to see them here.
            </p>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border bg-white">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left text-sm font-medium">Name</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Type</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Role</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Site</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-4 py-3 text-left text-sm font-medium">Serial</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device) => (
                <tr key={device.id} className="border-b last:border-0 hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <a
                      href={`http://localhost:8000/dcim/devices/${device.id}/`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-primary hover:underline"
                    >
                      {device.name}
                    </a>
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {(device as any).device_type_name || "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {(device as any).role_name || "-"}
                  </td>
                  <td className="px-4 py-3 text-sm text-muted-foreground">
                    {(device as any).site_name || "-"}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${getStatusColor(device.status)}`}>
                      {device.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm font-mono text-muted-foreground">
                    {device.serial || "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="border-t px-4 py-3 text-sm text-muted-foreground">
            Total: {devices.length} devices
          </div>
        </div>
      )}
    </div>
  );
}
