"use client"

import { useCallback } from "react"
import { Upload } from "lucide-react"
import { cn } from "@/lib/utils"

interface DropzoneProps {
  onFilesSelected: (files: File[]) => void
  accept?: string
  multiple?: boolean
  maxSize?: number
  disabled?: boolean
  className?: string
}

export function Dropzone({
  onFilesSelected,
  accept = ".pdf,.docx",
  multiple = true,
  maxSize = 10 * 1024 * 1024, // 10MB default
  disabled = false,
  className,
}: DropzoneProps) {
  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault()
      e.stopPropagation()

      if (disabled) return

      const files = Array.from(e.dataTransfer.files)
      const validFiles = files.filter((file) => {
        if (maxSize && file.size > maxSize) return false
        if (accept) {
          const extensions = accept.split(",").map((ext) => ext.trim())
          const fileExt = `.${file.name.split(".").pop()?.toLowerCase()}`
          return extensions.includes(fileExt)
        }
        return true
      })

      if (validFiles.length > 0) {
        onFilesSelected(validFiles)
      }
    },
    [onFilesSelected, accept, maxSize, disabled]
  )

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files
      if (files && files.length > 0) {
        onFilesSelected(Array.from(files))
      }
      // Reset input value to allow selecting the same file again
      e.target.value = ""
    },
    [onFilesSelected]
  )

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      className={cn(
        "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
        disabled
          ? "border-gray-200 bg-gray-50 cursor-not-allowed"
          : "border-gray-300 hover:border-primary bg-gray-50/50 hover:bg-gray-50 cursor-pointer",
        className
      )}
    >
      <input
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileInput}
        disabled={disabled}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
      />

      <div className="flex flex-col items-center gap-2">
        <div className={cn(
          "w-12 h-12 rounded-full flex items-center justify-center",
          disabled ? "bg-gray-200" : "bg-primary/10"
        )}>
          <Upload className={cn(
            "w-6 h-6",
            disabled ? "text-gray-400" : "text-primary"
          )} />
        </div>

        <div className="space-y-1">
          <p className={cn(
            "text-sm font-medium",
            disabled ? "text-gray-400" : "text-gray-700"
          )}>
            Drop files here or click to browse
          </p>
          <p className="text-xs text-gray-500">
            {accept.replace(/\./g, "").toUpperCase()} files up to{" "}
            {Math.round(maxSize / 1024 / 1024)}MB
          </p>
        </div>
      </div>
    </div>
  )
}
