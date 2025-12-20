"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { EvaluationTable } from "@/components/evaluations/evaluation-table"
import { EvaluationFilters } from "@/components/evaluations/evaluation-filters"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { Plus } from "lucide-react"
import { EvaluationStatus } from "@/components/evaluations/status-badge"

export default function EvaluationsPage() {
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState({
    search: "",
    status: "ALL" as EvaluationStatus | "ALL",
    dateFrom: "",
    dateTo: "",
  })

  const itemsPerPage = 10

  // Mock data - in real app, this would come from API
  const allEvaluations = [
    {
      id: "1",
      referenceId: "RFP-2024-001",
      title: "IT Infrastructure Modernization",
      department: "IT Department",
      status: "COMPLETED" as const,
      createdAt: "2024-12-15",
      updatedAt: "2024-12-18",
      vendorCount: 5,
    },
    {
      id: "2",
      referenceId: "RFP-2024-002",
      title: "Cloud Services Procurement",
      department: "IT Department",
      status: "PROCESSING" as const,
      createdAt: "2024-12-18",
      updatedAt: "2024-12-20",
      vendorCount: 3,
    },
    {
      id: "3",
      referenceId: "RFP-2024-003",
      title: "Cybersecurity Assessment Tools",
      department: "Security",
      status: "PENDING_DOCUMENTS" as const,
      createdAt: "2024-12-19",
      updatedAt: "2024-12-19",
      vendorCount: 4,
    },
    {
      id: "4",
      referenceId: "RFP-2024-004",
      title: "Data Analytics Platform",
      department: "Analytics",
      status: "DRAFT" as const,
      createdAt: "2024-12-20",
      updatedAt: "2024-12-20",
      vendorCount: 2,
    },
    {
      id: "5",
      referenceId: "RFP-2024-005",
      title: "Enterprise Resource Planning System",
      department: "Finance",
      status: "COMPLETED" as const,
      createdAt: "2024-12-10",
      updatedAt: "2024-12-14",
      vendorCount: 6,
    },
    {
      id: "6",
      referenceId: "RFP-2024-006",
      title: "Customer Relationship Management",
      department: "Sales",
      status: "PROCESSING" as const,
      createdAt: "2024-12-12",
      updatedAt: "2024-12-18",
      vendorCount: 4,
    },
    {
      id: "7",
      referenceId: "RFP-2024-007",
      title: "Network Security Upgrade",
      department: "Security",
      status: "COMPLETED" as const,
      createdAt: "2024-12-08",
      updatedAt: "2024-12-11",
      vendorCount: 3,
    },
    {
      id: "8",
      referenceId: "RFP-2024-008",
      title: "Document Management System",
      department: "Administration",
      status: "DRAFT" as const,
      createdAt: "2024-12-20",
      updatedAt: "2024-12-20",
      vendorCount: 2,
    },
    {
      id: "9",
      referenceId: "RFP-2024-009",
      title: "Video Conferencing Solution",
      department: "IT Department",
      status: "PENDING_DOCUMENTS" as const,
      createdAt: "2024-12-17",
      updatedAt: "2024-12-19",
      vendorCount: 5,
    },
    {
      id: "10",
      referenceId: "RFP-2024-010",
      title: "Help Desk Ticketing System",
      department: "IT Department",
      status: "PROCESSING" as const,
      createdAt: "2024-12-16",
      updatedAt: "2024-12-20",
      vendorCount: 3,
    },
  ]

  // Apply filters
  const filteredEvaluations = allEvaluations.filter((evaluation) => {
    // Search filter
    if (
      filters.search &&
      !evaluation.referenceId.toLowerCase().includes(filters.search.toLowerCase()) &&
      !evaluation.title.toLowerCase().includes(filters.search.toLowerCase())
    ) {
      return false
    }

    // Status filter
    if (filters.status !== "ALL" && evaluation.status !== filters.status) {
      return false
    }

    // Date range filter
    if (filters.dateFrom && evaluation.createdAt < filters.dateFrom) {
      return false
    }
    if (filters.dateTo && evaluation.createdAt > filters.dateTo) {
      return false
    }

    return true
  })

  // Pagination
  const totalPages = Math.ceil(filteredEvaluations.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentEvaluations = filteredEvaluations.slice(startIndex, endIndex)

  const handleFilterChange = (newFilters: typeof filters) => {
    setFilters(newFilters)
    setCurrentPage(1) // Reset to first page when filters change
  }

  const handleDelete = (id: string) => {
    // In real app, this would call an API
    console.log("Delete evaluation:", id)
    alert("Delete functionality would be implemented here")
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Evaluations</h1>
          <p className="text-muted-foreground">
            Manage and track all your vendor bid evaluations
          </p>
        </div>
        <Link href="/evaluations/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Evaluation
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <EvaluationFilters onFilterChange={handleFilterChange} />

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        Showing {startIndex + 1}-{Math.min(endIndex, filteredEvaluations.length)} of{" "}
        {filteredEvaluations.length} evaluations
      </div>

      {/* Table */}
      <EvaluationTable evaluations={currentEvaluations} onDelete={handleDelete} />

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  setCurrentPage((prev) => Math.max(1, prev - 1))
                }}
              />
            </PaginationItem>

            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
              // Show first page, last page, current page, and pages around current
              if (
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 1 && page <= currentPage + 1)
              ) {
                return (
                  <PaginationItem key={page}>
                    <PaginationLink
                      href="#"
                      onClick={(e) => {
                        e.preventDefault()
                        setCurrentPage(page)
                      }}
                      isActive={page === currentPage}
                    >
                      {page}
                    </PaginationLink>
                  </PaginationItem>
                )
              } else if (
                page === currentPage - 2 ||
                page === currentPage + 2
              ) {
                return <PaginationEllipsis key={page} />
              }
              return null
            })}

            <PaginationItem>
              <PaginationNext
                href="#"
                onClick={(e) => {
                  e.preventDefault()
                  setCurrentPage((prev) => Math.min(totalPages, prev + 1))
                }}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  )
}
