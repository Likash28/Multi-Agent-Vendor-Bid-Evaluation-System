"use client"

import { useState } from "react"
import { Dropzone } from "@/components/file-upload/dropzone"
import { FileList, FileItem } from "@/components/file-upload/file-list"
import { WizardData } from "../wizard-container"
import { useToast } from "@/hooks/use-toast"

interface DocumentsStepProps {
  data: WizardData
  updateData: (data: Partial<WizardData>) => void
}

export function DocumentsStep({ data, updateData }: DocumentsStepProps) {
  const { toast } = useToast()
  const [fileItems, setFileItems] = useState<FileItem[]>(
    data.documents.map((file, index) => ({
      id: `file-${index}-${file.name}`,
      file,
      progress: 100,
      status: "success" as const,
    }))
  )

  const handleFilesSelected = (files: File[]) => {
    const maxSize = 10 * 1024 * 1024 // 10MB

    const validFiles = files.filter((file) => {
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: `${file.name} exceeds the 10MB limit`,
          variant: "destructive",
        })
        return false
      }
      return true
    })

    if (validFiles.length === 0) return

    const newFileItems: FileItem[] = validFiles.map((file) => ({
      id: `file-${Date.now()}-${Math.random()}-${file.name}`,
      file,
      progress: 0,
      status: "uploading",
    }))

    setFileItems((prev) => [...prev, ...newFileItems])

    // Simulate upload progress
    newFileItems.forEach((fileItem) => {
      simulateUpload(fileItem.id)
    })

    // Update wizard data
    const allFiles = [...data.documents, ...validFiles]
    updateData({ documents: allFiles })
  }

  const simulateUpload = (fileId: string) => {
    let progress = 0
    const interval = setInterval(() => {
      progress += 10
      setFileItems((prev) =>
        prev.map((item) =>
          item.id === fileId
            ? {
                ...item,
                progress: Math.min(progress, 100),
                status: progress >= 100 ? "success" : "uploading",
              }
            : item
        )
      )

      if (progress >= 100) {
        clearInterval(interval)
      }
    }, 100)
  }

  const handleRemoveFile = (id: string) => {
    const fileItem = fileItems.find((item) => item.id === id)
    if (!fileItem) return

    setFileItems((prev) => prev.filter((item) => item.id !== id))

    // Update wizard data
    const updatedFiles = data.documents.filter(
      (file) => file !== fileItem.file
    )
    updateData({ documents: updatedFiles })

    toast({
      title: "File removed",
      description: `${fileItem.file.name} has been removed`,
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Upload Documents
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Upload supporting documents for evaluation (optional)
        </p>
      </div>

      <div className="space-y-4">
        {/* Dropzone */}
        <Dropzone
          onFilesSelected={handleFilesSelected}
          accept=".pdf,.docx"
          multiple={true}
          maxSize={10 * 1024 * 1024}
        />

        {/* File List */}
        {fileItems.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold">
                Uploaded Files ({fileItems.length})
              </h3>
            </div>
            <FileList files={fileItems} onRemove={handleRemoveFile} />
          </div>
        )}

        {/* Info Box */}
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            Supported Formats
          </h4>
          <ul className="text-xs text-blue-800 space-y-1">
            <li>PDF documents (.pdf)</li>
            <li>Microsoft Word documents (.docx)</li>
            <li>Maximum file size: 10MB per file</li>
            <li>You can upload multiple files</li>
          </ul>
        </div>

        {/* Optional Note */}
        <p className="text-xs text-gray-500 text-center">
          These documents are optional and can include evaluation criteria,
          scoring rubrics, or reference materials
        </p>
      </div>
    </div>
  )
}
