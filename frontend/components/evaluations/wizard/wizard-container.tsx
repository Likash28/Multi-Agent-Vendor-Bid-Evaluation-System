"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { StepIndicator, WIZARD_STEPS } from "./step-indicator"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, Save } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export interface WizardData {
  // Step 1: Basic Info
  title: string
  description: string
  tenderDocument?: File

  // Step 2: Configuration
  evaluationMethod: "L1" | "QCBS" | "TWO_STAGE"
  technicalWeight: number
  financialWeight: number
  qualificationThreshold: number
  enableComplianceCheck: boolean
  enableAIJustifications: boolean
  enableCartelDetection: boolean

  // Step 3: Documents
  documents: File[]

  // Step 4: Vendors
  vendors: Array<{
    id: string
    name: string
    gstin: string
    contact: string
    bidDocument?: File
  }>
}

const STORAGE_KEY = "govprocure-evaluation-wizard"

const initialData: WizardData = {
  title: "",
  description: "",
  evaluationMethod: "QCBS",
  technicalWeight: 70,
  financialWeight: 30,
  qualificationThreshold: 75,
  enableComplianceCheck: true,
  enableAIJustifications: true,
  enableCartelDetection: false,
  documents: [],
  vendors: [],
}

interface WizardContainerProps {
  children: (props: {
    data: WizardData
    currentStep: number
    updateData: (data: Partial<WizardData>) => void
    goToNext: () => void
    goToPrevious: () => void
    goToStep: (step: number) => void
  }) => React.ReactNode
}

export function WizardContainer({ children }: WizardContainerProps) {
  const router = useRouter()
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(1)
  const [completedSteps, setCompletedSteps] = useState<number[]>([])
  const [data, setData] = useState<WizardData>(initialData)

  // Load data from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        // Note: Files can't be stored in localStorage, so we only restore non-file data
        setData((prev) => ({
          ...prev,
          ...parsed,
          tenderDocument: undefined,
          documents: [],
          vendors: parsed.vendors?.map((v: any) => ({
            ...v,
            bidDocument: undefined,
          })) || [],
        }))
      } catch (error) {
        console.error("Failed to load wizard data:", error)
      }
    }
  }, [])

  // Save data to localStorage whenever it changes
  useEffect(() => {
    // Create a serializable copy (excluding File objects)
    const serializable = {
      ...data,
      tenderDocument: undefined,
      documents: [],
      vendors: data.vendors.map((v) => ({
        ...v,
        bidDocument: undefined,
      })),
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(serializable))
  }, [data])

  const updateData = useCallback((updates: Partial<WizardData>) => {
    setData((prev) => ({ ...prev, ...updates }))
  }, [])

  const validateStep = useCallback(
    (step: number): boolean => {
      switch (step) {
        case 1:
          if (!data.title || data.title.length < 10) {
            toast({
              title: "Validation Error",
              description: "Title must be at least 10 characters long",
              variant: "destructive",
            })
            return false
          }
          return true

        case 2:
          if (data.technicalWeight + data.financialWeight !== 100) {
            toast({
              title: "Validation Error",
              description: "Technical and financial weights must sum to 100",
              variant: "destructive",
            })
            return false
          }
          return true

        case 3:
          // Documents are optional
          return true

        case 4:
          if (data.vendors.length === 0) {
            toast({
              title: "Validation Error",
              description: "Please add at least one vendor",
              variant: "destructive",
            })
            return false
          }
          return true

        case 5:
          // Review step - no validation needed
          return true

        default:
          return true
      }
    },
    [data, toast]
  )

  const goToNext = useCallback(() => {
    if (validateStep(currentStep)) {
      if (!completedSteps.includes(currentStep)) {
        setCompletedSteps((prev) => [...prev, currentStep])
      }
      if (currentStep < WIZARD_STEPS.length) {
        setCurrentStep((prev) => prev + 1)
        window.scrollTo({ top: 0, behavior: "smooth" })
      }
    }
  }, [currentStep, completedSteps, validateStep])

  const goToPrevious = useCallback(() => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1)
      window.scrollTo({ top: 0, behavior: "smooth" })
    }
  }, [currentStep])

  const goToStep = useCallback(
    (step: number) => {
      if (completedSteps.includes(step) || step < currentStep) {
        setCurrentStep(step)
        window.scrollTo({ top: 0, behavior: "smooth" })
      }
    },
    [completedSteps, currentStep]
  )

  const handleSaveDraft = useCallback(() => {
    toast({
      title: "Draft Saved",
      description: "Your progress has been saved to your browser",
    })
  }, [toast])

  const clearWizardData = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    setData(initialData)
    setCompletedSteps([])
    setCurrentStep(1)
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Create New Evaluation
        </h1>
        <p className="mt-2 text-gray-600">
          Follow the steps to set up your vendor bid evaluation
        </p>
      </div>

      {/* Step Indicator */}
      <div className="mb-8">
        <StepIndicator
          currentStep={currentStep}
          completedSteps={completedSteps}
          onStepClick={goToStep}
        />
      </div>

      {/* Step Content */}
      <Card className="p-6 mb-6">
        {children({ data, currentStep, updateData, goToNext, goToPrevious, goToStep })}
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div>
          {currentStep > 1 && (
            <Button
              type="button"
              variant="outline"
              onClick={goToPrevious}
              className="gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleSaveDraft}
            className="gap-2"
          >
            <Save className="w-4 h-4" />
            Save Draft
          </Button>

          {currentStep < WIZARD_STEPS.length && (
            <Button type="button" onClick={goToNext} className="gap-2">
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
