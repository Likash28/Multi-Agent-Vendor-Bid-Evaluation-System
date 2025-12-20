"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  FileText,
  Settings,
  Upload,
  Building2,
  Edit,
  Send,
  Clock,
  CheckCircle2,
} from "lucide-react"
import { WizardData } from "../wizard-container"
import { useToast } from "@/hooks/use-toast"

interface ReviewStepProps {
  data: WizardData
  goToStep: (step: number) => void
}

export function ReviewStep({ data, goToStep }: ReviewStepProps) {
  const router = useRouter()
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const getEvaluationMethodLabel = (method: string) => {
    switch (method) {
      case "L1":
        return "L1 (Lowest Price)"
      case "QCBS":
        return "QCBS (Quality and Cost Based)"
      case "TWO_STAGE":
        return "Two-Stage"
      default:
        return method
    }
  }

  const estimatedTime = () => {
    const baseTime = 5 // minutes
    const vendorTime = data.vendors.length * 2
    const documentTime = data.documents.length * 1
    const total = baseTime + vendorTime + documentTime

    if (total < 60) {
      return `${total} minutes`
    }
    const hours = Math.floor(total / 60)
    const minutes = total % 60
    return `${hours}h ${minutes}m`
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Clear wizard data from localStorage
      localStorage.removeItem("govprocure-evaluation-wizard")

      toast({
        title: "Evaluation Created",
        description: "Your evaluation has been submitted successfully",
      })

      // Redirect to processing page
      router.push("/evaluations/123/processing")
    } catch (error) {
      toast({
        title: "Submission Failed",
        description: "There was an error creating the evaluation",
        variant: "destructive",
      })
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Review & Submit
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Review your evaluation details before submitting
        </p>
      </div>

      <div className="space-y-4">
        {/* Basic Info */}
        <Card className="p-4">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Basic Information</h3>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => goToStep(1)}
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>

          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-600">Title:</span>
              <p className="font-medium mt-1">{data.title}</p>
            </div>

            {data.description && (
              <div>
                <span className="text-gray-600">Description:</span>
                <p className="text-gray-700 mt-1">{data.description}</p>
              </div>
            )}

            {data.tenderDocument && (
              <div>
                <span className="text-gray-600">Tender Document:</span>
                <p className="text-gray-700 mt-1 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-500" />
                  {data.tenderDocument.name}
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Configuration */}
        <Card className="p-4">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <Settings className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Configuration</h3>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => goToStep(2)}
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>

          <div className="space-y-3 text-sm">
            <div>
              <span className="text-gray-600">Evaluation Method:</span>
              <p className="font-medium mt-1">
                {getEvaluationMethodLabel(data.evaluationMethod)}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-gray-600">Technical Weight:</span>
                <p className="font-medium mt-1">{data.technicalWeight}%</p>
              </div>
              <div>
                <span className="text-gray-600">Financial Weight:</span>
                <p className="font-medium mt-1">{data.financialWeight}%</p>
              </div>
            </div>

            <div>
              <span className="text-gray-600">Qualification Threshold:</span>
              <p className="font-medium mt-1">
                {data.qualificationThreshold}%
              </p>
            </div>

            <div>
              <span className="text-gray-600">Advanced Features:</span>
              <div className="flex flex-wrap gap-2 mt-2">
                {data.enableComplianceCheck && (
                  <Badge variant="secondary">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Compliance Check
                  </Badge>
                )}
                {data.enableAIJustifications && (
                  <Badge variant="secondary">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    AI Justifications
                  </Badge>
                )}
                {data.enableCartelDetection && (
                  <Badge variant="secondary">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    Cartel Detection
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </Card>

        {/* Documents */}
        <Card className="p-4">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">
                Documents ({data.documents.length})
              </h3>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => goToStep(3)}
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>

          {data.documents.length > 0 ? (
            <ul className="space-y-2 text-sm">
              {data.documents.map((doc, index) => (
                <li
                  key={index}
                  className="flex items-center gap-2 text-gray-700"
                >
                  <FileText className="w-4 h-4 text-blue-500" />
                  {doc.name}
                  <span className="text-xs text-gray-500">
                    ({(doc.size / 1024).toFixed(2)} KB)
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No documents uploaded</p>
          )}
        </Card>

        {/* Vendors */}
        <Card className="p-4">
          <div className="flex items-start justify-between gap-3 mb-3">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-primary" />
              <h3 className="font-semibold">Vendors ({data.vendors.length})</h3>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => goToStep(4)}
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>

          <div className="space-y-3">
            {data.vendors.map((vendor, index) => (
              <div
                key={vendor.id}
                className="p-3 bg-gray-50 rounded-lg text-sm"
              >
                <p className="font-medium">{vendor.name}</p>
                <p className="text-gray-600 text-xs mt-1">
                  GSTIN: {vendor.gstin}
                </p>
                <p className="text-gray-600 text-xs">
                  Contact: {vendor.contact}
                </p>
                {vendor.bidDocument && (
                  <div className="flex items-center gap-1 mt-2 text-xs text-blue-600">
                    <FileText className="w-3 h-3" />
                    {vendor.bidDocument.name}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Processing Time Estimate */}
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <Clock className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-900 text-sm">
                Estimated Processing Time
              </h3>
              <p className="text-blue-700 text-sm mt-1">
                Approximately {estimatedTime()}
              </p>
              <p className="text-blue-600 text-xs mt-2">
                You'll receive notifications as the evaluation progresses
              </p>
            </div>
          </div>
        </Card>

        {/* Submit Button */}
        <Button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full h-12 text-base"
          size="lg"
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Creating Evaluation...
            </>
          ) : (
            <>
              <Send className="w-5 h-5 mr-2" />
              Submit Evaluation
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
