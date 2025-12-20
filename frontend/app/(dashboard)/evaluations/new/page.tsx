"use client"

import { WizardContainer } from "@/components/evaluations/wizard/wizard-container"
import { BasicInfoStep } from "@/components/evaluations/wizard/steps/basic-info-step"
import { ConfigStep } from "@/components/evaluations/wizard/steps/config-step"
import { DocumentsStep } from "@/components/evaluations/wizard/steps/documents-step"
import { VendorsStep } from "@/components/evaluations/wizard/steps/vendors-step"
import { ReviewStep } from "@/components/evaluations/wizard/steps/review-step"

export default function NewEvaluationPage() {
  return (
    <WizardContainer>
      {({ data, currentStep, updateData, goToStep }) => {
        switch (currentStep) {
          case 1:
            return <BasicInfoStep data={data} updateData={updateData} />
          case 2:
            return <ConfigStep data={data} updateData={updateData} />
          case 3:
            return <DocumentsStep data={data} updateData={updateData} />
          case 4:
            return <VendorsStep data={data} updateData={updateData} />
          case 5:
            return <ReviewStep data={data} goToStep={goToStep} />
          default:
            return <BasicInfoStep data={data} updateData={updateData} />
        }
      }}
    </WizardContainer>
  )
}
