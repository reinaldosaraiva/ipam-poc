import { Network, Server, Layers, Activity } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
  change?: string;
}

function StatCard({ title, value, icon, change }: StatCardProps) {
  return (
    <div className="rounded-lg border bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {change && (
            <p className="text-xs text-green-600">{change}</p>
          )}
        </div>
        <div className="rounded-full bg-primary/10 p-3">
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your network infrastructure
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="IP Prefixes"
          value="--"
          icon={<Network className="h-6 w-6 text-primary" />}
          change="Loading..."
        />
        <StatCard
          title="VLANs"
          value="--"
          icon={<Layers className="h-6 w-6 text-primary" />}
        />
        <StatCard
          title="Devices"
          value="--"
          icon={<Server className="h-6 w-6 text-primary" />}
        />
        <StatCard
          title="Active"
          value="--"
          icon={<Activity className="h-6 w-6 text-primary" />}
        />
      </div>

      <div className="rounded-lg border bg-white p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <p className="text-muted-foreground">
          Connect to NetBox to view recent changes.
        </p>
      </div>
    </div>
  );
}
