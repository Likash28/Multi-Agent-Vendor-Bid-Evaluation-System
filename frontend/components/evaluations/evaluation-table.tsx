"use client"

import Link from "next/link"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { StatusBadge, EvaluationStatus } from "./status-badge"
import { formatDate } from "@/lib/utils"
import { Eye, Edit, Trash2, ArrowUpDown } from "lucide-react"
import { useState } from "react"

interface Evaluation {
  id: string
  referenceId: string
  title: string
  status: EvaluationStatus
  createdAt: string
  updatedAt: string
  vendorCount: number
  department: string
}

interface EvaluationTableProps {
  evaluations: Evaluation[]
  onDelete?: (id: string) => void
}

type SortField = "referenceId" | "title" | "status" | "createdAt" | "vendorCount"
type SortDirection = "asc" | "desc"

export function EvaluationTable({ evaluations, onDelete }: EvaluationTableProps) {
  const [sortField, setSortField] = useState<SortField>("createdAt")
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc")

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc")
    } else {
      setSortField(field)
      setSortDirection("asc")
    }
  }

  const sortedEvaluations = [...evaluations].sort((a, b) => {
    let aValue = a[sortField]
    let bValue = b[sortField]

    // Handle string comparison
    if (typeof aValue === "string" && typeof bValue === "string") {
      aValue = aValue.toLowerCase()
      bValue = bValue.toLowerCase()
    }

    if (sortDirection === "asc") {
      return aValue > bValue ? 1 : -1
    } else {
      return aValue < bValue ? 1 : -1
    }
  })

  const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
    <button
      onClick={() => handleSort(field)}
      className="flex items-center gap-2 hover:text-foreground"
    >
      {children}
      <ArrowUpDown className="h-4 w-4" />
    </button>
  )

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>
              <SortButton field="referenceId">Reference ID</SortButton>
            </TableHead>
            <TableHead>
              <SortButton field="title">Title</SortButton>
            </TableHead>
            <TableHead>Department</TableHead>
            <TableHead>
              <SortButton field="status">Status</SortButton>
            </TableHead>
            <TableHead>
              <SortButton field="createdAt">Created</SortButton>
            </TableHead>
            <TableHead>
              <SortButton field="vendorCount">Vendors</SortButton>
            </TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedEvaluations.length === 0 ? (
            <TableRow>
              <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                No evaluations found
              </TableCell>
            </TableRow>
          ) : (
            sortedEvaluations.map((evaluation) => (
              <TableRow key={evaluation.id}>
                <TableCell className="font-medium">
                  {evaluation.referenceId}
                </TableCell>
                <TableCell className="max-w-xs truncate">
                  {evaluation.title}
                </TableCell>
                <TableCell>{evaluation.department}</TableCell>
                <TableCell>
                  <StatusBadge status={evaluation.status} />
                </TableCell>
                <TableCell>{formatDate(evaluation.createdAt)}</TableCell>
                <TableCell>{evaluation.vendorCount}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Link href={`/evaluations/${evaluation.id}`}>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </Link>
                    {evaluation.status === "DRAFT" && (
                      <Link href={`/evaluations/${evaluation.id}/edit`}>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                      </Link>
                    )}
                    {onDelete && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onDelete(evaluation.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}
