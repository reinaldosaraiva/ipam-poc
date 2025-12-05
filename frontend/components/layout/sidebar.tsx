"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Network,
  Layers,
  Server,
  Settings,
  Cable,
  Building2,
  Users,
  Wand2,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Allocation", href: "/allocation", icon: Wand2, highlight: true },
  { name: "Prefixes", href: "/prefixes", icon: Network },
  { name: "VLANs", href: "/vlans", icon: Layers },
  { name: "Sites", href: "/sites", icon: Building2 },
  { name: "Tenants", href: "/tenants", icon: Users },
  { name: "Devices", href: "/devices", icon: Server },
  { name: "Interfaces", href: "/interfaces", icon: Cable },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r bg-white">
      <div className="flex h-16 items-center border-b px-6">
        <Network className="h-8 w-8 text-primary" />
        <span className="ml-2 text-xl font-bold">IPAM</span>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="h-5 w-5" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">
          IPAM PoC v0.1.0
        </p>
      </div>
    </div>
  );
}
