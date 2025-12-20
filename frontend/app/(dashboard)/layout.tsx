"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()

  useEffect(() => {
    // Auth guard - check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
    }
  }, [router])

  // Mock user data - in real app, this would come from auth context/store
  const user = {
    name: "John Doe",
    email: "john.doe@gov.example.com",
    avatar: undefined,
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Header */}
        <Header user={user} />

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-muted/10 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
