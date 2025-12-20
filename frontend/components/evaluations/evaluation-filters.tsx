"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Search, X } from "lucide-react"
import { EvaluationStatus } from "./status-badge"

interface EvaluationFiltersProps {
  onFilterChange: (filters: {
    search: string
    status: EvaluationStatus | "ALL"
    dateFrom: string
    dateTo: string
  }) => void
}

export function EvaluationFilters({ onFilterChange }: EvaluationFiltersProps) {
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState<EvaluationStatus | "ALL">("ALL")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")

  const handleApplyFilters = () => {
    onFilterChange({ search, status, dateFrom, dateTo })
  }

  const handleClearFilters = () => {
    setSearch("")
    setStatus("ALL")
    setDateFrom("")
    setDateTo("")
    onFilterChange({ search: "", status: "ALL", dateFrom: "", dateTo: "" })
  }

  const hasActiveFilters = search || status !== "ALL" || dateFrom || dateTo

  return (
    <div className="space-y-4 rounded-lg border bg-card p-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search evaluations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        {/* Status Filter */}
        <Select value={status} onValueChange={(value) => setStatus(value as EvaluationStatus | "ALL")}>
          <SelectTrigger>
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Statuses</SelectItem>
            <SelectItem value="DRAFT">Draft</SelectItem>
            <SelectItem value="PENDING_DOCUMENTS">Pending Documents</SelectItem>
            <SelectItem value="PROCESSING">Processing</SelectItem>
            <SelectItem value="COMPLETED">Completed</SelectItem>
            <SelectItem value="CANCELLED">Cancelled</SelectItem>
          </SelectContent>
        </Select>

        {/* Date From */}
        <Input
          type="date"
          placeholder="From Date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
        />

        {/* Date To */}
        <Input
          type="date"
          placeholder="To Date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button onClick={handleApplyFilters} size="sm">
          <Search className="mr-2 h-4 w-4" />
          Apply Filters
        </Button>
        {hasActiveFilters && (
          <Button onClick={handleClearFilters} variant="outline" size="sm">
            <X className="mr-2 h-4 w-4" />
            Clear Filters
          </Button>
        )}
      </div>
    </div>
  )
}
