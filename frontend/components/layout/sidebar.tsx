"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  FileSearch,
  Building,
  FileText,
  Settings,
  ChevronLeft,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { useState } from "react"

const navigation = [
  {
    name: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Evaluations",
    href: "/evaluations",
    icon: FileSearch,
  },
  {
    name: "Vendors",
    href: "/vendors",
    icon: Building,
  },
  {
    name: "Reports",
    href: "/reports",
    icon: FileText,
  },
  {
    name: "Settings",
    href: "/settings",
    icon: Settings,
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div
      className={cn(
        "flex flex-col border-r bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between border-b px-4">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">G</span>
            </div>
            <span className="font-bold text-lg">GovProcure</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/dashboard" className="flex items-center">
            <div className="h-8 w-8 rounded-md bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-lg">G</span>
            </div>
          </Link>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "h-8 w-8 transition-transform",
            collapsed ? "rotate-180" : ""
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
          const Icon = item.icon

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                collapsed ? "justify-center" : "justify-start"
              )}
              title={collapsed ? item.name : undefined}
            >
              <Icon className={cn("h-5 w-5 flex-shrink-0", !collapsed && "mr-3")} />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t p-4">
        {!collapsed && (
          <div className="text-xs text-muted-foreground">
            <p>Version 1.0.0</p>
          </div>
        )}
      </div>
    </div>
  )
}
