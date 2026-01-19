"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X, Loader2 } from "lucide-react"
import { WizardData } from "../wizard-container"
import { useState } from "react"
import { uploadDocument } from "@/lib/evaluation-api"
import { useToast } from "@/hooks/use-toast"

const schema = z.object({
  title: z.string().min(10, "Title must be at least 10 characters"),
  description: z.string().optional(),
})

type FormData = z.infer<typeof schema>

interface BasicInfoStepProps {
  data: WizardData
  updateData: (data: Partial<WizardData>) => void
}

export function BasicInfoStep({ data, updateData }: BasicInfoStepProps) {
  const { toast } = useToast()
  const [tenderFile, setTenderFile] = useState<File | undefined>(
    data.tenderDocument
  )
  const [tenderDocumentId, setTenderDocumentId] = useState<string | undefined>(
    data.tenderDocumentId
  )
  const [isUploading, setIsUploading] = useState(false)

  const {
    register,
    formState: { errors },
    setValue,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: data.title,
      description: data.description,
    },
  })

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setValue("title", value)
    updateData({ title: value })
  }

  const handleDescriptionChange = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    const value = e.target.value
    setValue("description", value)
    updateData({ description: value })
  }

  const handleTenderFileChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = [".pdf", ".docx"]
    const fileExt = `.${file.name.split(".").pop()?.toLowerCase()}`
    if (!validTypes.includes(fileExt)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF or DOCX file",
        variant: "destructive",
      })
      return
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024
    if (file.size > maxSize) {
      toast({
        title: "File too large",
        description: "File size must be less than 50MB",
        variant: "destructive",
      })
      return
    }

    setTenderFile(file)
    setIsUploading(true)

    try {
      // Upload document to backend
      const response = await uploadDocument(file, "tender")
      setTenderDocumentId(response.id)
      updateData({
        tenderDocument: file,
        tenderDocumentId: response.id,
      })

      toast({
        title: "Document uploaded",
        description: `${file.name} has been uploaded successfully`,
      })
    } catch (error: any) {
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload document",
        variant: "destructive",
      })
      setTenderFile(undefined)
    } finally {
      setIsUploading(false)
    }
  }

  const removeTenderFile = () => {
    setTenderFile(undefined)
    setTenderDocumentId(undefined)
    updateData({ tenderDocument: undefined, tenderDocumentId: undefined })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Basic Information
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Provide the basic details for your evaluation
        </p>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div className="space-y-2">
          <Label htmlFor="title" className="text-sm font-medium">
            Evaluation Title <span className="text-red-500">*</span>
          </Label>
          <Input
            id="title"
            {...register("title")}
            onChange={handleTitleChange}
            placeholder="e.g., Office Supplies Procurement 2024"
            className={errors.title ? "border-red-500" : ""}
          />
          {errors.title && (
            <p className="text-sm text-red-500">{errors.title.message}</p>
          )}
          <p className="text-xs text-gray-500">
            Minimum 10 characters required
          </p>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description" className="text-sm font-medium">
            Description
          </Label>
          <Textarea
            id="description"
            {...register("description")}
            onChange={handleDescriptionChange}
            placeholder="Optional: Provide additional details about this evaluation"
            rows={4}
            className="resize-none"
          />
          <p className="text-xs text-gray-500">
            Optional: Add any relevant context or notes
          </p>
        </div>

        {/* Tender Document */}
        <div className="space-y-2">
          <Label htmlFor="tender-document" className="text-sm font-medium">
            Tender Document
          </Label>

          {!tenderFile ? (
            <div className="relative">
              <input
                type="file"
                id="tender-document"
                accept=".pdf,.docx"
                onChange={handleTenderFileChange}
                disabled={isUploading}
                className="sr-only"
              />
              <label
                htmlFor="tender-document"
                className={`flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg transition-colors ${
                  isUploading
                    ? "cursor-not-allowed opacity-50"
                    : "cursor-pointer hover:border-primary hover:bg-gray-50"
                }`}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                    <span className="text-sm text-gray-600">Uploading...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-600">
                      Upload tender document (PDF, DOCX)
                    </span>
                  </>
                )}
              </label>
            </div>
          ) : (
            <div className="flex items-center gap-3 p-3 border rounded-lg bg-gray-50">
              <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {tenderFile.name}
                </p>
                <p className="text-xs text-gray-500">
                  {(tenderFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={removeTenderFile}
                className="h-8 w-8 p-0"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          )}

          <p className="text-xs text-gray-500">
            Optional: Upload the main tender/RFP document
          </p>
        </div>
      </div>
    </div>
  )
}
