"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import {
  Plus,
  Trash2,
  Upload,
  FileText,
  X,
  Building2,
  Search,
} from "lucide-react"
import { WizardData } from "../wizard-container"
import { useToast } from "@/hooks/use-toast"

const vendorSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  gstin: z
    .string()
    .regex(
      /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
      "Invalid GSTIN format"
    ),
  contact: z.string().min(10, "Contact must be at least 10 characters"),
})

type VendorFormData = z.infer<typeof vendorSchema>

interface VendorsStepProps {
  data: WizardData
  updateData: (data: Partial<WizardData>) => void
}

export function VendorsStep({ data, updateData }: VendorsStepProps) {
  const { toast } = useToast()
  const [showAddForm, setShowAddForm] = useState(data.vendors.length === 0)
  const [editingVendorId, setEditingVendorId] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<VendorFormData>({
    resolver: zodResolver(vendorSchema),
  })

  const onAddVendor = (formData: VendorFormData) => {
    const newVendor = {
      id: `vendor-${Date.now()}-${Math.random()}`,
      name: formData.name,
      gstin: formData.gstin,
      contact: formData.contact,
    }

    updateData({ vendors: [...data.vendors, newVendor] })
    reset()
    setShowAddForm(false)

    toast({
      title: "Vendor added",
      description: `${formData.name} has been added to the evaluation`,
    })
  }

  const handleRemoveVendor = (vendorId: string) => {
    const vendor = data.vendors.find((v) => v.id === vendorId)
    updateData({ vendors: data.vendors.filter((v) => v.id !== vendorId) })

    toast({
      title: "Vendor removed",
      description: `${vendor?.name} has been removed`,
    })
  }

  const handleBidDocumentUpload = (
    vendorId: string,
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0]
    if (!file) return

    updateData({
      vendors: data.vendors.map((v) =>
        v.id === vendorId ? { ...v, bidDocument: file } : v
      ),
    })

    const vendor = data.vendors.find((v) => v.id === vendorId)
    toast({
      title: "Bid document uploaded",
      description: `${file.name} uploaded for ${vendor?.name}`,
    })
  }

  const handleRemoveBidDocument = (vendorId: string) => {
    updateData({
      vendors: data.vendors.map((v) =>
        v.id === vendorId ? { ...v, bidDocument: undefined } : v
      ),
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Add Vendors</h2>
        <p className="mt-1 text-sm text-gray-600">
          Add vendors who will participate in this evaluation
        </p>
      </div>

      <div className="space-y-4">
        {/* Vendor List */}
        {data.vendors.length > 0 && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold">
                Vendors ({data.vendors.length})
              </h3>
            </div>

            {data.vendors.map((vendor) => (
              <Card key={vendor.id} className="p-4">
                <div className="space-y-3">
                  {/* Vendor Info */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Building2 className="w-5 h-5 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-sm truncate">
                          {vendor.name}
                        </h4>
                        <p className="text-xs text-gray-600">
                          GSTIN: {vendor.gstin}
                        </p>
                        <p className="text-xs text-gray-600">
                          Contact: {vendor.contact}
                        </p>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveVendor(vendor.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>

                  {/* Bid Document Upload */}
                  <div className="pl-13">
                    {!vendor.bidDocument ? (
                      <div className="relative">
                        <input
                          type="file"
                          id={`bid-${vendor.id}`}
                          accept=".pdf,.docx"
                          onChange={(e) =>
                            handleBidDocumentUpload(vendor.id, e)
                          }
                          className="sr-only"
                        />
                        <label
                          htmlFor={`bid-${vendor.id}`}
                          className="flex items-center gap-2 px-3 py-2 text-sm border border-dashed rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                        >
                          <Upload className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">
                            Upload bid document
                          </span>
                        </label>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 p-2 border rounded-lg bg-gray-50">
                        <FileText className="w-4 h-4 text-blue-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium truncate">
                            {vendor.bidDocument.name}
                          </p>
                          <p className="text-xs text-gray-500">
                            {(vendor.bidDocument.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveBidDocument(vendor.id)}
                          className="h-6 w-6 p-0"
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Add Vendor Form */}
        {showAddForm ? (
          <Card className="p-4 border-2 border-primary/20">
            <form onSubmit={handleSubmit(onAddVendor)} className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold">Add New Vendor</h3>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowAddForm(false)
                    reset()
                  }}
                >
                  Cancel
                </Button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Vendor Name */}
                <div className="space-y-2">
                  <Label htmlFor="vendor-name" className="text-sm">
                    Vendor Name <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="vendor-name"
                    {...register("name")}
                    placeholder="e.g., ABC Corporation"
                    className={errors.name ? "border-red-500" : ""}
                  />
                  {errors.name && (
                    <p className="text-xs text-red-500">
                      {errors.name.message}
                    </p>
                  )}
                </div>

                {/* GSTIN */}
                <div className="space-y-2">
                  <Label htmlFor="vendor-gstin" className="text-sm">
                    GSTIN <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="vendor-gstin"
                    {...register("gstin")}
                    placeholder="e.g., 22AAAAA0000A1Z5"
                    className={errors.gstin ? "border-red-500" : ""}
                  />
                  {errors.gstin && (
                    <p className="text-xs text-red-500">
                      {errors.gstin.message}
                    </p>
                  )}
                </div>

                {/* Contact */}
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="vendor-contact" className="text-sm">
                    Contact Information <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="vendor-contact"
                    {...register("contact")}
                    placeholder="e.g., contact@abc.com or +91-9876543210"
                    className={errors.contact ? "border-red-500" : ""}
                  />
                  {errors.contact && (
                    <p className="text-xs text-red-500">
                      {errors.contact.message}
                    </p>
                  )}
                </div>
              </div>

              <Button type="submit" className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add Vendor
              </Button>
            </form>
          </Card>
        ) : (
          <Button
            type="button"
            variant="outline"
            onClick={() => setShowAddForm(true)}
            className="w-full border-dashed"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Vendor
          </Button>
        )}

        {/* Search Existing Vendors - Placeholder */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search existing vendors (coming soon)"
            disabled
            className="pl-9"
          />
        </div>

        {/* Info */}
        {data.vendors.length === 0 && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              You need to add at least one vendor to proceed with the
              evaluation.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
