"use client"

import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

export interface Step {
  id: number
  name: string
  description: string
}

export const WIZARD_STEPS: Step[] = [
  { id: 1, name: "Basic Info", description: "Evaluation details" },
  { id: 2, name: "Configuration", description: "Scoring settings" },
  { id: 3, name: "Documents", description: "Upload files" },
  { id: 4, name: "Vendors", description: "Add vendors" },
  { id: 5, name: "Review", description: "Confirm details" },
]

interface StepIndicatorProps {
  currentStep: number
  completedSteps: number[]
  onStepClick?: (step: number) => void
}

export function StepIndicator({
  currentStep,
  completedSteps,
  onStepClick,
}: StepIndicatorProps) {
  const isStepComplete = (stepId: number) => completedSteps.includes(stepId)
  const isStepCurrent = (stepId: number) => currentStep === stepId
  const isStepClickable = (stepId: number) =>
    isStepComplete(stepId) || stepId < currentStep

  return (
    <nav aria-label="Progress">
      <ol className="flex items-center justify-between">
        {WIZARD_STEPS.map((step, stepIdx) => {
          const isComplete = isStepComplete(step.id)
          const isCurrent = isStepCurrent(step.id)
          const isClickable = isStepClickable(step.id)

          return (
            <li
              key={step.id}
              className={cn(
                "relative",
                stepIdx !== WIZARD_STEPS.length - 1 && "flex-1"
              )}
            >
              {/* Connector line */}
              {stepIdx !== WIZARD_STEPS.length - 1 && (
                <div
                  className={cn(
                    "absolute top-5 left-[calc(50%+1.5rem)] w-[calc(100%-3rem)] h-0.5",
                    isComplete ? "bg-primary" : "bg-gray-200"
                  )}
                  aria-hidden="true"
                />
              )}

              {/* Step button */}
              <button
                type="button"
                onClick={() => isClickable && onStepClick?.(step.id)}
                disabled={!isClickable}
                className={cn(
                  "group relative flex flex-col items-center",
                  isClickable && "cursor-pointer",
                  !isClickable && "cursor-not-allowed"
                )}
              >
                {/* Step circle */}
                <div
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors",
                    isComplete &&
                      "border-primary bg-primary text-white",
                    isCurrent &&
                      !isComplete &&
                      "border-primary bg-white text-primary",
                    !isCurrent &&
                      !isComplete &&
                      "border-gray-300 bg-white text-gray-500",
                    isClickable && "group-hover:border-primary"
                  )}
                >
                  {isComplete ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <span className="text-sm font-semibold">{step.id}</span>
                  )}
                </div>

                {/* Step text */}
                <div className="mt-2 text-center">
                  <p
                    className={cn(
                      "text-sm font-medium",
                      isCurrent ? "text-primary" : "text-gray-700"
                    )}
                  >
                    {step.name}
                  </p>
                  <p className="text-xs text-gray-500 hidden sm:block">
                    {step.description}
                  </p>
                </div>
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
