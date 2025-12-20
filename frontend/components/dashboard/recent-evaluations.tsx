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
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { StatusBadge, EvaluationStatus } from "@/components/evaluations/status-badge"
import { formatDate } from "@/lib/utils"
import { Eye } from "lucide-react"

interface Evaluation {
  id: string
  referenceId: string
  title: string
  status: EvaluationStatus
  createdAt: string
  vendorCount: number
}

interface RecentEvaluationsProps {
  evaluations: Evaluation[]
}

export function RecentEvaluations({ evaluations }: RecentEvaluationsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Evaluations</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Reference ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Vendors</TableHead>
              <TableHead className="text-right">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {evaluations.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  No evaluations found
                </TableCell>
              </TableRow>
            ) : (
              evaluations.map((evaluation) => (
                <TableRow key={evaluation.id}>
                  <TableCell className="font-medium">
                    {evaluation.referenceId}
                  </TableCell>
                  <TableCell>{evaluation.title}</TableCell>
                  <TableCell>
                    <StatusBadge status={evaluation.status} />
                  </TableCell>
                  <TableCell>{formatDate(evaluation.createdAt)}</TableCell>
                  <TableCell>{evaluation.vendorCount}</TableCell>
                  <TableCell className="text-right">
                    <Link href={`/evaluations/${evaluation.id}`}>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View
                      </Button>
                    </Link>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
