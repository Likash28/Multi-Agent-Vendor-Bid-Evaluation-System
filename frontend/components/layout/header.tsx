"use client"

import { Bell, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { UserMenu } from "./user-menu"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"

interface HeaderProps {
  title?: string
  showSearch?: boolean
  user?: {
    name: string
    email: string
    avatar?: string
  }
}

export function Header({ title, showSearch = true, user }: HeaderProps) {
  // Mock notifications for demo
  const notifications = [
    {
      id: 1,
      title: "Evaluation Complete",
      message: "RFP-2024-001 evaluation has been completed",
      time: "5 min ago",
      read: false,
    },
    {
      id: 2,
      title: "New Vendor Registered",
      message: "Tech Solutions Inc. has registered",
      time: "1 hour ago",
      read: false,
    },
    {
      id: 3,
      title: "Document Uploaded",
      message: "Vendor submitted required documents",
      time: "2 hours ago",
      read: true,
    },
  ]

  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <header className="sticky top-0 z-40 border-b bg-background">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Left section - Title */}
        <div className="flex items-center gap-4">
          {title && <h1 className="text-xl font-semibold">{title}</h1>}
        </div>

        {/* Middle section - Search */}
        {showSearch && (
          <div className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                type="search"
                placeholder="Search evaluations, vendors..."
                className="pl-9"
              />
            </div>
          </div>
        )}

        {/* Right section - Notifications and User */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
                  >
                    {unreadCount}
                  </Badge>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel className="flex items-center justify-between">
                <span>Notifications</span>
                {unreadCount > 0 && (
                  <Badge variant="secondary" className="ml-auto">
                    {unreadCount} new
                  </Badge>
                )}
              </DropdownMenuLabel>
              <div className="max-h-96 overflow-y-auto">
                {notifications.map((notification) => (
                  <DropdownMenuItem
                    key={notification.id}
                    className="flex flex-col items-start p-3 cursor-pointer"
                  >
                    <div className="flex items-start justify-between w-full">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{notification.title}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {notification.time}
                        </p>
                      </div>
                      {!notification.read && (
                        <div className="h-2 w-2 rounded-full bg-primary flex-shrink-0 mt-1" />
                      )}
                    </div>
                  </DropdownMenuItem>
                ))}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <UserMenu user={user} />
        </div>
      </div>
    </header>
  )
}
