"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { createOrGetVendor } from "@/lib/vendor-api"

const vendorSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  gstin: z
    .string()
    .optional()
    .refine(
      (val) => !val || /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(val),
      "Invalid GSTIN format"
    ),
  registration_no: z.string().optional(),
  contact_email: z
    .string()
    .optional()
    .refine(
      (val) => !val || z.string().email().safeParse(val).success,
      "Invalid email format"
    ),
  contact_phone: z.string().optional(),
  address: z.string().optional(),
})

type VendorFormData = z.infer<typeof vendorSchema>

export default function NewVendorPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VendorFormData>({
    resolver: zodResolver(vendorSchema),
    defaultValues: {
      name: "",
      gstin: "",
      registration_no: "",
      contact_email: "",
      contact_phone: "",
      address: "",
    },
  })

  const onSubmit = async (formData: VendorFormData) => {
    setIsSubmitting(true)
    try {
      const vendorData = {
        name: formData.name,
        gstin: formData.gstin || undefined,
        registration_no: formData.registration_no || undefined,
        contact_email: formData.contact_email || undefined,
        contact_phone: formData.contact_phone || undefined,
        address: formData.address || undefined,
      }

      const vendor = await createOrGetVendor(vendorData)

      toast({
        title: "Vendor added successfully",
        description: `${vendor.name} has been ${vendor.id ? "created" : "found"} in the system.`,
      })

      // Redirect to vendor detail page or vendors list
      router.push(`/vendors/${vendor.id}`)
    } catch (error: any) {
      toast({
        title: "Failed to add vendor",
        description: error.message || "Could not create vendor. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Add New Vendor</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Create a new vendor or find an existing one by GSTIN or name
          </p>
        </div>
      </div>

      {/* Form */}
      <Card className="p-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Vendor Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="text-sm font-medium">
              Vendor Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="name"
              {...register("name")}
              placeholder="e.g., ABC Corporation"
              className={errors.name ? "border-red-500" : ""}
            />
            {errors.name && (
              <p className="text-xs text-red-500">{errors.name.message}</p>
            )}
          </div>

          {/* GSTIN and Registration No */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="gstin" className="text-sm font-medium">
                GSTIN
              </Label>
              <Input
                id="gstin"
                {...register("gstin")}
                placeholder="e.g., 22AAAAA0000A1Z5"
                className={errors.gstin ? "border-red-500" : ""}
              />
              {errors.gstin && (
                <p className="text-xs text-red-500">{errors.gstin.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="registration_no" className="text-sm font-medium">
                Registration Number
              </Label>
              <Input
                id="registration_no"
                {...register("registration_no")}
                placeholder="e.g., U12345AB2023"
                className={errors.registration_no ? "border-red-500" : ""}
              />
              {errors.registration_no && (
                <p className="text-xs text-red-500">
                  {errors.registration_no.message}
                </p>
              )}
            </div>
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact_email" className="text-sm font-medium">
                Email
              </Label>
              <Input
                id="contact_email"
                type="email"
                {...register("contact_email")}
                placeholder="e.g., contact@abc.com"
                className={errors.contact_email ? "border-red-500" : ""}
              />
              {errors.contact_email && (
                <p className="text-xs text-red-500">
                  {errors.contact_email.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="contact_phone" className="text-sm font-medium">
                Phone
              </Label>
              <Input
                id="contact_phone"
                {...register("contact_phone")}
                placeholder="e.g., +91-9876543210"
                className={errors.contact_phone ? "border-red-500" : ""}
              />
              {errors.contact_phone && (
                <p className="text-xs text-red-500">
                  {errors.contact_phone.message}
                </p>
              )}
            </div>
          </div>

          {/* Address */}
          <div className="space-y-2">
            <Label htmlFor="address" className="text-sm font-medium">
              Address
            </Label>
            <Input
              id="address"
              {...register("address")}
              placeholder="e.g., 123 Main St, City, State, PIN"
              className={errors.address ? "border-red-500" : ""}
            />
            {errors.address && (
              <p className="text-xs text-red-500">{errors.address.message}</p>
            )}
          </div>

          {/* Info */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> If a vendor with the same GSTIN or name
              already exists, the existing vendor will be returned instead of
              creating a duplicate.
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                "Create Vendor"
              )}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  )
}

