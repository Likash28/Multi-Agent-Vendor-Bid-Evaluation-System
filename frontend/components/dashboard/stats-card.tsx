import { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  icon: LucideIcon
  change?: {
    value: number
    trend: "up" | "down"
  }
  variant?: "default" | "primary" | "success" | "warning" | "danger"
}

const variantStyles = {
  default: "bg-background",
  primary: "bg-blue-50 border-blue-200",
  success: "bg-green-50 border-green-200",
  warning: "bg-yellow-50 border-yellow-200",
  danger: "bg-red-50 border-red-200",
}

const iconVariantStyles = {
  default: "bg-muted text-muted-foreground",
  primary: "bg-blue-100 text-blue-600",
  success: "bg-green-100 text-green-600",
  warning: "bg-yellow-100 text-yellow-600",
  danger: "bg-red-100 text-red-600",
}

export function StatsCard({
  title,
  value,
  icon: Icon,
  change,
  variant = "default",
}: StatsCardProps) {
  return (
    <Card className={cn(variantStyles[variant])}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={cn("h-8 w-8 rounded-md flex items-center justify-center", iconVariantStyles[variant])}>
          <Icon className="h-4 w-4" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <div className="flex items-center text-xs text-muted-foreground mt-1">
            {change.trend === "up" ? (
              <TrendingUp className="mr-1 h-3 w-3 text-green-600" />
            ) : (
              <TrendingDown className="mr-1 h-3 w-3 text-red-600" />
            )}
            <span
              className={cn(
                change.trend === "up" ? "text-green-600" : "text-red-600"
              )}
            >
              {change.value}%
            </span>
            <span className="ml-1">from last month</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
