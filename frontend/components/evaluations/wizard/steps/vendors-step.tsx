"use client"

import { useState, useEffect } from "react"
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
import { createOrGetVendor, searchVendors, type Vendor } from "@/lib/vendor-api"
import { uploadDocument } from "@/lib/evaluation-api"
import { Loader2 } from "lucide-react"

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
  const [uploadingVendors, setUploadingVendors] = useState<Set<string>>(new Set())
  const [uploadingDocuments, setUploadingDocuments] = useState<Set<string>>(new Set())
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<Vendor[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSearchResults, setShowSearchResults] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<VendorFormData>({
    resolver: zodResolver(vendorSchema),
  })

  const onAddVendor = async (formData: VendorFormData) => {
    const tempId = `vendor-${Date.now()}-${Math.random()}`
    const newVendor = {
      id: tempId,
      name: formData.name,
      gstin: formData.gstin,
      contact: formData.contact,
    }

    // Add vendor to list immediately (optimistic update)
    updateData({ vendors: [...data.vendors, newVendor] })
    setUploadingVendors((prev) => new Set(prev).add(tempId))

    try {
      // Extract email or phone from contact
      const isEmail = formData.contact.includes("@")
      const vendorData = {
        name: formData.name,
        gstin: formData.gstin,
        contact_email: isEmail ? formData.contact : undefined,
        contact_phone: !isEmail ? formData.contact : undefined,
      }

      // Create or get vendor from backend
      const vendor = await createOrGetVendor(vendorData)

      // Update vendor with API ID
      updateData({
        vendors: data.vendors.map((v) =>
          v.id === tempId ? { ...v, vendorId: vendor.id } : v
        ),
      })

      reset()
      setShowAddForm(false)

      toast({
        title: "Vendor added",
        description: `${formData.name} has been added to the evaluation`,
      })
    } catch (error: any) {
      // Remove vendor on error
      updateData({
        vendors: data.vendors.filter((v) => v.id !== tempId),
      })

      toast({
        title: "Failed to add vendor",
        description: error.message || "Could not create vendor",
        variant: "destructive",
      })
    } finally {
      setUploadingVendors((prev) => {
        const next = new Set(prev)
        next.delete(tempId)
        return next
      })
    }
  }

  const handleRemoveVendor = (vendorId: string) => {
    const vendor = data.vendors.find((v) => v.id === vendorId)
    updateData({ vendors: data.vendors.filter((v) => v.id !== vendorId) })

    toast({
      title: "Vendor removed",
      description: `${vendor?.name} has been removed`,
    })
  }

  const handleBidDocumentUpload = async (
    vendorId: string,
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

    // Update vendor with file (optimistic update)
    updateData({
      vendors: data.vendors.map((v) =>
        v.id === vendorId ? { ...v, bidDocument: file } : v
      ),
    })

    setUploadingDocuments((prev) => new Set(prev).add(vendorId))

    try {
      // Upload document to backend
      const response = await uploadDocument(file, "bid", {
        vendor_id: data.vendors.find((v) => v.id === vendorId)?.vendorId,
      })

      // Update vendor with document ID
      updateData({
        vendors: data.vendors.map((v) =>
          v.id === vendorId
            ? { ...v, bidDocument: file, bidDocumentId: response.id }
            : v
        ),
      })

      const vendor = data.vendors.find((v) => v.id === vendorId)
      toast({
        title: "Bid document uploaded",
        description: `${file.name} uploaded for ${vendor?.name}`,
      })
    } catch (error: any) {
      // Remove file on error
      updateData({
        vendors: data.vendors.map((v) =>
          v.id === vendorId ? { ...v, bidDocument: undefined } : v
        ),
      })

      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload document",
        variant: "destructive",
      })
    } finally {
      setUploadingDocuments((prev) => {
        const next = new Set(prev)
        next.delete(vendorId)
        return next
      })
    }
  }

  const handleRemoveBidDocument = (vendorId: string) => {
    updateData({
      vendors: data.vendors.map((v) =>
        v.id === vendorId ? { ...v, bidDocument: undefined } : v
      ),
    })
  }

  // Search vendors
  const handleSearchVendors = async (query: string) => {
    if (!query || query.trim().length < 2) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }

    setIsSearching(true)
    setShowSearchResults(true)

    try {
      const response = await searchVendors(query.trim())
      // Filter out vendors that are already added
      const existingVendorIds = new Set(
        data.vendors.map((v) => v.vendorId).filter(Boolean)
      )
      const filteredResults = response.items.filter(
        (v) => !existingVendorIds.has(v.id)
      )
      setSearchResults(filteredResults)
    } catch (error: any) {
      toast({
        title: "Search failed",
        description: error.message || "Could not search vendors",
        variant: "destructive",
      })
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  // Handle search input change with debounce
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }

    const timer = setTimeout(() => {
      handleSearchVendors(searchQuery)
    }, 300)

    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery])

  // Add existing vendor from search results
  const handleAddExistingVendor = async (vendor: Vendor) => {
    const tempId = `vendor-${Date.now()}-${Math.random()}`
    const contact = vendor.contact_email || vendor.contact_phone || ""
    
    const newVendor = {
      id: tempId,
      vendorId: vendor.id,
      name: vendor.name,
      gstin: vendor.gstin || "",
      contact: contact,
    }

    // Add vendor to list immediately
    updateData({ vendors: [...data.vendors, newVendor] })

    setSearchQuery("")
    setSearchResults([])
    setShowSearchResults(false)

    toast({
      title: "Vendor added",
      description: `${vendor.name} has been added to the evaluation`,
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
                          disabled={uploadingDocuments.has(vendor.id)}
                          className="sr-only"
                        />
                        <label
                          htmlFor={`bid-${vendor.id}`}
                          className={`flex items-center gap-2 px-3 py-2 text-sm border border-dashed rounded-lg transition-colors ${
                            uploadingDocuments.has(vendor.id)
                              ? "cursor-not-allowed opacity-50"
                              : "cursor-pointer hover:bg-gray-50"
                          }`}
                        >
                          {uploadingDocuments.has(vendor.id) ? (
                            <>
                              <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
                              <span className="text-gray-600">Uploading...</span>
                            </>
                          ) : (
                            <>
                              <Upload className="w-4 h-4 text-gray-400" />
                              <span className="text-gray-600">
                                Upload bid document
                              </span>
                            </>
                          )}
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

              <Button
                type="submit"
                className="w-full"
                disabled={uploadingVendors.size > 0}
              >
                {uploadingVendors.size > 0 ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Vendor
                  </>
                )}
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

        {/* Search Existing Vendors */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search existing vendors..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => {
              if (searchResults.length > 0 && searchQuery.length >= 2) {
                setShowSearchResults(true)
              }
            }}
            onBlur={() => {
              // Delay hiding to allow click on results
              setTimeout(() => setShowSearchResults(false), 200)
            }}
            className="pl-9"
          />
          {isSearching && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 animate-spin" />
          )}

          {/* Search Results Dropdown */}
          {showSearchResults && searchResults.length > 0 && (
            <Card className="absolute z-10 w-full mt-1 max-h-60 overflow-y-auto shadow-lg">
              <div className="p-2 space-y-1">
                {searchResults.map((vendor) => (
                  <button
                    key={vendor.id}
                    type="button"
                    onMouseDown={(e) => {
                      // Prevent onBlur from firing before onClick
                      e.preventDefault()
                    }}
                    onClick={() => handleAddExistingVendor(vendor)}
                    className="w-full text-left p-3 hover:bg-gray-50 rounded-lg transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Building2 className="w-4 h-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate">
                          {vendor.name}
                        </p>
                        {vendor.gstin && (
                          <p className="text-xs text-gray-600">
                            GSTIN: {vendor.gstin}
                          </p>
                        )}
                        {(vendor.contact_email || vendor.contact_phone) && (
                          <p className="text-xs text-gray-600">
                            {vendor.contact_email || vendor.contact_phone}
                          </p>
                        )}
                      </div>
                      <Plus className="w-4 h-4 text-primary flex-shrink-0 mt-1" />
                    </div>
                  </button>
                ))}
              </div>
            </Card>
          )}

          {showSearchResults && searchQuery.length >= 2 && !isSearching && searchResults.length === 0 && (
            <Card className="absolute z-10 w-full mt-1 shadow-lg">
              <div className="p-4 text-center text-sm text-gray-500">
                No vendors found matching "{searchQuery}"
              </div>
            </Card>
          )}
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
