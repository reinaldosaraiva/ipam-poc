"use client";

import { useState } from "react";
import { Layers, Play, Eye, CheckCircle, AlertCircle } from "lucide-react";
import { allocationApi, AllocationPlan, NamingPreview } from "@/lib/api";

export default function AllocationPage() {
  const [siteName, setSiteName] = useState("Site Nordeste");
  const [regionCode, setRegionCode] = useState("ne");
  const [baseNetwork, setBaseNetwork] = useState("10.1");
  const [rackCount, setRackCount] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<NamingPreview | null>(null);
  const [plan, setPlan] = useState<AllocationPlan | null>(null);
  const [success, setSuccess] = useState(false);

  const handlePreview = async () => {
    try {
      setLoading(true);
      setError(null);
      const [namingPreview, allocationPlan] = await Promise.all([
        allocationApi.previewNaming({
          site_name: siteName,
          region_code: regionCode,
          rack_count: rackCount,
        }),
        allocationApi.createPlan({
          base_network: baseNetwork,
          rack_count: rackCount,
          create_vlans: true,
          dry_run: true,
        }),
      ]);
      setPreview(namingPreview);
      setPlan(allocationPlan);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate preview");
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    try {
      setLoading(true);
      setError(null);
      await allocationApi.allocateSite({
        site_name: siteName,
        region_code: regionCode,
        base_network: baseNetwork,
        rack_count: rackCount,
        dry_run: false,
      });
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to execute allocation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Site Allocation</h1>
        <p className="text-muted-foreground">
          Allocate a complete site with naming conventions and IP planning
        </p>
      </div>

      {success && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4 flex items-center gap-3">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <span className="text-green-700">Site allocated successfully! Check NetBox for the created resources.</span>
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Form */}
        <div className="rounded-lg border bg-white p-6">
          <h2 className="text-lg font-semibold mb-4">Site Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Site Name</label>
              <input
                type="text"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 text-sm"
                placeholder="Site Nordeste"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Region Code</label>
              <select
                value={regionCode}
                onChange={(e) => setRegionCode(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 text-sm"
              >
                <option value="ne">NE - Nordeste</option>
                <option value="se">SE - Sudeste</option>
                <option value="s">S - Sul</option>
                <option value="n">N - Norte</option>
                <option value="co">CO - Centro-Oeste</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Base Network</label>
              <input
                type="text"
                value={baseNetwork}
                onChange={(e) => setBaseNetwork(e.target.value)}
                className="w-full rounded-lg border px-3 py-2 text-sm"
                placeholder="10.0"
              />
              <p className="mt-1 text-xs text-muted-foreground">
                First two octets (e.g., 10.0, 172.16, 192.168)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Rack Count</label>
              <input
                type="number"
                value={rackCount}
                onChange={(e) => setRackCount(parseInt(e.target.value) || 1)}
                min={1}
                max={50}
                className="w-full rounded-lg border px-3 py-2 text-sm"
              />
            </div>

            <div className="flex gap-3 pt-4">
              <button
                onClick={handlePreview}
                disabled={loading}
                className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg border bg-white px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
              >
                <Eye className="h-4 w-4" />
                Preview
              </button>
              <button
                onClick={handleExecute}
                disabled={loading || !plan}
                className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 disabled:opacity-50"
              >
                <Play className="h-4 w-4" />
                Execute
              </button>
            </div>
          </div>
        </div>

        {/* Naming Preview */}
        {preview && (
          <div className="rounded-lg border bg-white p-6">
            <h2 className="text-lg font-semibold mb-4">Naming Preview</h2>

            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <span className="text-muted-foreground">Site:</span>
                <span className="font-mono">{preview.site.name}</span>
                <span className="text-muted-foreground">Slug:</span>
                <span className="font-mono">{preview.site.slug}</span>
                <span className="text-muted-foreground">Tenant:</span>
                <span className="font-mono">{preview.tenant.name}</span>
                <span className="text-muted-foreground">Facility:</span>
                <span className="font-mono">{preview.facility_code}</span>
              </div>

              <div>
                <h3 className="font-medium mb-2">Racks</h3>
                <div className="flex flex-wrap gap-2">
                  {preview.racks.map((rack) => (
                    <span key={rack} className="rounded bg-muted px-2 py-1 font-mono text-xs">
                      {rack}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="font-medium mb-2">Device Names</h3>
                <div className="grid grid-cols-2 gap-2">
                  <span className="text-muted-foreground">Spine:</span>
                  <span className="font-mono">{preview.devices.spine}</span>
                  <span className="text-muted-foreground">Leaf:</span>
                  <span className="font-mono">{preview.devices.leaf}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Allocation Plan */}
      {plan && (
        <div className="rounded-lg border bg-white p-6">
          <h2 className="text-lg font-semibold mb-4">Allocation Plan</h2>

          <div className="grid gap-6 lg:grid-cols-3">
            {/* Summary */}
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-3">Summary</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Container:</span>
                  <span className="font-mono">{plan.container_prefix}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">VLAN Subnets:</span>
                  <span>{plan.vlan_subnets.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Host Subnets:</span>
                  <span>{plan.host_subnets.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">VLANs:</span>
                  <span>{plan.vlans_to_create.length}</span>
                </div>
                <div className="flex justify-between font-medium pt-2 border-t">
                  <span>Total Prefixes:</span>
                  <span>{plan.total_prefixes}</span>
                </div>
              </div>
            </div>

            {/* VLAN Subnets */}
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-3">VLAN Subnets (/21)</h3>
              <div className="space-y-2 text-sm max-h-48 overflow-y-auto">
                {plan.vlan_subnets.slice(0, 6).map((subnet) => (
                  <div key={subnet.prefix} className="flex items-center gap-2">
                    <span className="font-mono text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                      {subnet.vlan_vid}
                    </span>
                    <span className="font-mono text-xs">{subnet.prefix}</span>
                  </div>
                ))}
                {plan.vlan_subnets.length > 6 && (
                  <p className="text-muted-foreground text-xs">
                    +{plan.vlan_subnets.length - 6} more...
                  </p>
                )}
              </div>
            </div>

            {/* VLANs */}
            <div className="rounded-lg border p-4">
              <h3 className="font-medium mb-3">VLANs to Create</h3>
              <div className="space-y-2 text-sm max-h-48 overflow-y-auto">
                {plan.vlans_to_create.slice(0, 6).map((vlan) => (
                  <div key={vlan.vid} className="flex items-center gap-2">
                    <span className={`font-mono text-xs px-1.5 py-0.5 rounded ${
                      vlan.category === 'management'
                        ? 'bg-purple-100 text-purple-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {vlan.vid}
                    </span>
                    <span className="text-xs truncate">{vlan.name}</span>
                  </div>
                ))}
                {plan.vlans_to_create.length > 6 && (
                  <p className="text-muted-foreground text-xs">
                    +{plan.vlans_to_create.length - 6} more...
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
