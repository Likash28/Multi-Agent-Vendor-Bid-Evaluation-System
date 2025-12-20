"use client"

import { FileSearch, CheckCircle, Clock, AlertCircle } from "lucide-react"
import { StatsCard } from "@/components/dashboard/stats-card"
import { RecentEvaluations } from "@/components/dashboard/recent-evaluations"
import { ActivityChart } from "@/components/dashboard/activity-chart"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Plus } from "lucide-react"

export default function DashboardPage() {
  // Mock data - in real app, this would come from API
  const stats = {
    total: 48,
    active: 12,
    completed: 32,
    pending: 4,
  }

  const recentEvaluations = [
    {
      id: "1",
      referenceId: "RFP-2024-001",
      title: "IT Infrastructure Modernization",
      status: "COMPLETED" as const,
      createdAt: "2024-12-15",
      vendorCount: 5,
    },
    {
      id: "2",
      referenceId: "RFP-2024-002",
      title: "Cloud Services Procurement",
      status: "PROCESSING" as const,
      createdAt: "2024-12-18",
      vendorCount: 3,
    },
    {
      id: "3",
      referenceId: "RFP-2024-003",
      title: "Cybersecurity Assessment Tools",
      status: "PENDING_DOCUMENTS" as const,
      createdAt: "2024-12-19",
      vendorCount: 4,
    },
    {
      id: "4",
      referenceId: "RFP-2024-004",
      title: "Data Analytics Platform",
      status: "DRAFT" as const,
      createdAt: "2024-12-20",
      vendorCount: 2,
    },
  ]

  const activityData = [
    { date: "Nov 20", evaluations: 4 },
    { date: "Nov 25", evaluations: 6 },
    { date: "Nov 30", evaluations: 3 },
    { date: "Dec 5", evaluations: 8 },
    { date: "Dec 10", evaluations: 5 },
    { date: "Dec 15", evaluations: 7 },
    { date: "Dec 20", evaluations: 9 },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's an overview of your evaluations.
          </p>
        </div>
        <Link href="/evaluations/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Evaluation
          </Button>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Evaluations"
          value={stats.total}
          icon={FileSearch}
          change={{ value: 12, trend: "up" }}
          variant="primary"
        />
        <StatsCard
          title="Active"
          value={stats.active}
          icon={Clock}
          change={{ value: 8, trend: "up" }}
          variant="warning"
        />
        <StatsCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle}
          change={{ value: 15, trend: "up" }}
          variant="success"
        />
        <StatsCard
          title="Pending Review"
          value={stats.pending}
          icon={AlertCircle}
          change={{ value: 5, trend: "down" }}
          variant="danger"
        />
      </div>

      {/* Charts and Tables */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ActivityChart data={activityData} />
        <div className="space-y-6">
          <div className="grid gap-4">
            <div className="rounded-lg border bg-card p-6">
              <h3 className="font-semibold mb-2">Quick Actions</h3>
              <div className="space-y-2">
                <Link href="/evaluations/new">
                  <Button variant="outline" className="w-full justify-start">
                    <Plus className="mr-2 h-4 w-4" />
                    Create New Evaluation
                  </Button>
                </Link>
                <Link href="/vendors">
                  <Button variant="outline" className="w-full justify-start">
                    <Plus className="mr-2 h-4 w-4" />
                    Add New Vendor
                  </Button>
                </Link>
                <Link href="/reports">
                  <Button variant="outline" className="w-full justify-start">
                    <FileSearch className="mr-2 h-4 w-4" />
                    View Reports
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Evaluations */}
      <RecentEvaluations evaluations={recentEvaluations} />
    </div>
  )
}
