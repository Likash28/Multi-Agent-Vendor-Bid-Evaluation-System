"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts"

interface ActivityChartProps {
  data: Array<{
    date: string
    evaluations: number
  }>
}

export function ActivityChart({ data }: ActivityChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Evaluation Activity (Last 30 Days)</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="rounded-lg border bg-background p-2 shadow-sm">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Date
                          </span>
                          <span className="font-bold text-muted-foreground">
                            {payload[0].payload.date}
                          </span>
                        </div>
                        <div className="flex flex-col">
                          <span className="text-[0.70rem] uppercase text-muted-foreground">
                            Evaluations
                          </span>
                          <span className="font-bold">
                            {payload[0].value}
                          </span>
                        </div>
                      </div>
                    </div>
                  )
                }
                return null
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="evaluations"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
