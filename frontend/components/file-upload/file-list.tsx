"use client"

import { FileText, X, CheckCircle2, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"

export interface FileItem {
  id: string
  file: File
  progress: number
  status: "pending" | "uploading" | "success" | "error"
  error?: string
}

interface FileListProps {
  files: FileItem[]
  onRemove: (id: string) => void
  className?: string
}

export function FileList({ files, onRemove, className }: FileListProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + " " + sizes[i]
  }

  const getFileIcon = (filename: string) => {
    const ext = filename.split(".").pop()?.toLowerCase()
    return <FileText className="w-5 h-5 text-blue-500" />
  }

  if (files.length === 0) {
    return null
  }

  return (
    <div className={cn("space-y-2", className)}>
      {files.map((fileItem) => (
        <div
          key={fileItem.id}
          className="flex items-center gap-3 p-3 rounded-lg border bg-card"
        >
          <div className="flex-shrink-0">
            {getFileIcon(fileItem.file.name)}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between gap-2 mb-1">
              <p className="text-sm font-medium truncate">
                {fileItem.file.name}
              </p>
              <span className="text-xs text-muted-foreground whitespace-nowrap">
                {formatFileSize(fileItem.file.size)}
              </span>
            </div>

            {fileItem.status === "uploading" && (
              <div className="space-y-1">
                <Progress value={fileItem.progress} className="h-1" />
                <p className="text-xs text-muted-foreground">
                  Uploading... {fileItem.progress}%
                </p>
              </div>
            )}

            {fileItem.status === "error" && (
              <p className="text-xs text-destructive">{fileItem.error}</p>
            )}

            {fileItem.status === "success" && (
              <div className="flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3 text-green-500" />
                <p className="text-xs text-green-600">Upload complete</p>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {fileItem.status === "uploading" && (
              <Loader2 className="w-4 h-4 animate-spin text-primary" />
            )}

            {fileItem.status === "success" && (
              <CheckCircle2 className="w-4 h-4 text-green-500" />
            )}

            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => onRemove(fileItem.id)}
              disabled={fileItem.status === "uploading"}
              className="h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
              <span className="sr-only">Remove file</span>
            </Button>
          </div>
        </div>
      ))}
    </div>
  )
}
