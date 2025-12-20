"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Upload, FileText, X } from "lucide-react"
import { WizardData } from "../wizard-container"
import { useState } from "react"

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
  const [tenderFile, setTenderFile] = useState<File | undefined>(
    data.tenderDocument
  )

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

  const handleTenderFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setTenderFile(file)
      updateData({ tenderDocument: file })
    }
  }

  const removeTenderFile = () => {
    setTenderFile(undefined)
    updateData({ tenderDocument: undefined })
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
                className="sr-only"
              />
              <label
                htmlFor="tender-document"
                className="flex items-center justify-center gap-2 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-primary hover:bg-gray-50 transition-colors"
              >
                <Upload className="w-5 h-5 text-gray-400" />
                <span className="text-sm text-gray-600">
                  Upload tender document (PDF, DOCX)
                </span>
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
