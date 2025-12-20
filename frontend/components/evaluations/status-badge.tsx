import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export type EvaluationStatus =
  | "DRAFT"
  | "PENDING_DOCUMENTS"
  | "PROCESSING"
  | "COMPLETED"
  | "CANCELLED"

interface StatusBadgeProps {
  status: EvaluationStatus
  className?: string
}

const statusConfig: Record<
  EvaluationStatus,
  { label: string; className: string }
> = {
  DRAFT: {
    label: "Draft",
    className: "bg-gray-100 text-gray-700 border-gray-300",
  },
  PENDING_DOCUMENTS: {
    label: "Pending Documents",
    className: "bg-yellow-100 text-yellow-700 border-yellow-300",
  },
  PROCESSING: {
    label: "Processing",
    className: "bg-blue-100 text-blue-700 border-blue-300 animate-pulse",
  },
  COMPLETED: {
    label: "Completed",
    className: "bg-green-100 text-green-700 border-green-300",
  },
  CANCELLED: {
    label: "Cancelled",
    className: "bg-red-100 text-red-700 border-red-300",
  },
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge className={cn(config.className, className)} variant="outline">
      {config.label}
    </Badge>
  )
}
