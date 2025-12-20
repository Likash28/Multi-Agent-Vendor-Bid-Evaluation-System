"use client"

import { useEffect } from "react"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Card } from "@/components/ui/card"
import { WizardData } from "../wizard-container"
import { FileCheck, Brain, AlertTriangle } from "lucide-react"

interface ConfigStepProps {
  data: WizardData
  updateData: (data: Partial<WizardData>) => void
}

export function ConfigStep({ data, updateData }: ConfigStepProps) {
  // Auto-calculate financial weight when technical weight changes
  useEffect(() => {
    updateData({ financialWeight: 100 - data.technicalWeight })
  }, [data.technicalWeight])

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Evaluation Configuration
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Configure how vendors will be evaluated
        </p>
      </div>

      <div className="space-y-6">
        {/* Evaluation Method */}
        <div className="space-y-3">
          <Label className="text-sm font-medium">
            Evaluation Method <span className="text-red-500">*</span>
          </Label>
          <RadioGroup
            value={data.evaluationMethod}
            onValueChange={(value) =>
              updateData({
                evaluationMethod: value as "L1" | "QCBS" | "TWO_STAGE",
              })
            }
            className="grid gap-3"
          >
            {/* L1 Method */}
            <label
              htmlFor="method-l1"
              className="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-primary/5"
            >
              <RadioGroupItem value="L1" id="method-l1" className="mt-1" />
              <div className="flex-1">
                <p className="font-medium text-sm">L1 (Lowest Price)</p>
                <p className="text-xs text-gray-600 mt-1">
                  Award to vendor with lowest qualifying bid
                </p>
              </div>
            </label>

            {/* QCBS Method */}
            <label
              htmlFor="method-qcbs"
              className="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-primary/5"
            >
              <RadioGroupItem value="QCBS" id="method-qcbs" className="mt-1" />
              <div className="flex-1">
                <p className="font-medium text-sm">
                  QCBS (Quality and Cost Based)
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Weighted evaluation of technical and financial proposals
                </p>
              </div>
            </label>

            {/* Two-Stage Method */}
            <label
              htmlFor="method-two-stage"
              className="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors has-[:checked]:border-primary has-[:checked]:bg-primary/5"
            >
              <RadioGroupItem
                value="TWO_STAGE"
                id="method-two-stage"
                className="mt-1"
              />
              <div className="flex-1">
                <p className="font-medium text-sm">Two-Stage</p>
                <p className="text-xs text-gray-600 mt-1">
                  Technical evaluation first, then financial for qualified
                  vendors
                </p>
              </div>
            </label>
          </RadioGroup>
        </div>

        {/* Weight Configuration */}
        <Card className="p-4 space-y-4 bg-gray-50">
          <h3 className="text-sm font-semibold">Scoring Weights</h3>

          {/* Technical Weight */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-sm">Technical Weight</Label>
              <span className="text-sm font-semibold text-primary">
                {data.technicalWeight}%
              </span>
            </div>
            <Slider
              value={[data.technicalWeight]}
              onValueChange={([value]) =>
                updateData({ technicalWeight: value })
              }
              min={0}
              max={100}
              step={5}
              className="w-full"
            />
          </div>

          {/* Financial Weight (Auto-calculated) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Label className="text-sm">Financial Weight</Label>
              <span className="text-sm font-semibold text-primary">
                {data.financialWeight}%
              </span>
            </div>
            <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${data.financialWeight}%` }}
              />
            </div>
            <p className="text-xs text-gray-500">
              Automatically calculated as 100 - Technical Weight
            </p>
          </div>
        </Card>

        {/* Qualification Threshold */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">
              Qualification Threshold
            </Label>
            <span className="text-sm font-semibold text-primary">
              {data.qualificationThreshold}%
            </span>
          </div>
          <Slider
            value={[data.qualificationThreshold]}
            onValueChange={([value]) =>
              updateData({ qualificationThreshold: value })
            }
            min={0}
            max={100}
            step={5}
            className="w-full"
          />
          <p className="text-xs text-gray-500">
            Minimum score required for technical qualification
          </p>
        </div>

        {/* Feature Toggles */}
        <div className="space-y-3 pt-2">
          <h3 className="text-sm font-semibold">Advanced Features</h3>

          {/* Compliance Check */}
          <div className="flex items-start gap-3 p-3 rounded-lg border">
            <FileCheck className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <Label htmlFor="compliance-check" className="text-sm font-medium cursor-pointer">
                  Enable Compliance Check
                </Label>
                <Switch
                  id="compliance-check"
                  checked={data.enableComplianceCheck}
                  onCheckedChange={(checked) =>
                    updateData({ enableComplianceCheck: checked })
                  }
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Verify vendor eligibility and document completeness
              </p>
            </div>
          </div>

          {/* AI Justifications */}
          <div className="flex items-start gap-3 p-3 rounded-lg border">
            <Brain className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <Label htmlFor="ai-justifications" className="text-sm font-medium cursor-pointer">
                  Enable AI Justifications
                </Label>
                <Switch
                  id="ai-justifications"
                  checked={data.enableAIJustifications}
                  onCheckedChange={(checked) =>
                    updateData({ enableAIJustifications: checked })
                  }
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Generate AI-powered explanations for scoring decisions
              </p>
            </div>
          </div>

          {/* Cartel Detection */}
          <div className="flex items-start gap-3 p-3 rounded-lg border">
            <AlertTriangle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <Label htmlFor="cartel-detection" className="text-sm font-medium cursor-pointer">
                  Enable Cartel Detection
                </Label>
                <Switch
                  id="cartel-detection"
                  checked={data.enableCartelDetection}
                  onCheckedChange={(checked) =>
                    updateData({ enableCartelDetection: checked })
                  }
                />
              </div>
              <p className="text-xs text-gray-600 mt-1">
                Analyze bid patterns for potential collusion
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
