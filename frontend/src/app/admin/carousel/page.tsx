"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { CarouselSlideForm } from "@/components/admin/CarouselSlideForm";
import { Button } from "@/components/ui/button";
import {
  createCarouselSlide,
  deleteCarouselSlide,
  getAdminCarouselSlides,
  reorderCarouselSlides,
  updateCarouselSlide,
} from "@/lib/admin-api";
import { IMAGE_PATHS } from "@/lib/imagePaths";
import { CarouselSlide } from "@/types";
import { CreateCarouselSlide } from "@/types/admin";
import Image from "next/image";
import { useEffect, useState } from "react";

const IMAGE_ERROR_FALLBACK_SRC =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='%23e5e7eb'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='12px' fill='%239ca3af'%3EError loading image%3C/text%3E%3C/svg%3E";

export default function AdminCarouselPage() {
  const [slides, setSlides] = useState<CarouselSlide[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSlide, setEditingSlide] = useState<CarouselSlide | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);
  const [failedImageIds, setFailedImageIds] = useState<Record<number, boolean>>(
    {},
  );

  const fetchSlides = async () => {
    setIsLoading(true);
    try {
      const response = await getAdminCarouselSlides();
      const sorted = (Array.isArray(response) ? response : []).sort(
        (a, b) => a.display_order - b.display_order,
      );
      setSlides(sorted);
    } catch (error) {
      console.error("Failed to fetch slides:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSlides();
  }, []);

  const handleEdit = (slide: CarouselSlide) => {
    setEditingSlide(slide);
    setIsFormOpen(true);
  };

  const handleDelete = async (slideId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this slide? This action cannot be undone.",
      )
    )
      return;
    try {
      await deleteCarouselSlide(slideId);
      fetchSlides();
    } catch (error) {
      console.error("Failed to delete slide:", error);
      alert("Failed to delete slide");
    }
  };

  const handleFormSubmit = async (formData: CreateCarouselSlide) => {
    setIsSaving(true);
    try {
      if (editingSlide) {
        await updateCarouselSlide(editingSlide.id, formData);
      } else {
        // Automatically append to the end
        formData.display_order =
          slides.length > 0
            ? Math.max(...slides.map((s) => s.display_order)) + 1
            : 0;
        await createCarouselSlide(formData);
      }
      setIsFormOpen(false);
      setEditingSlide(undefined);
      fetchSlides();
    } catch (error) {
      console.error("Failed to save slide:", error);
      alert("Failed to save slide");
    } finally {
      setIsSaving(false);
    }
  };

  const moveSlide = async (index: number, direction: "up" | "down") => {
    if (direction === "up" && index === 0) return;
    if (direction === "down" && index === slides.length - 1) return;

    const newSlides = [...slides];
    const targetIndex = direction === "up" ? index - 1 : index + 1;

    // Swap
    [newSlides[index], newSlides[targetIndex]] = [
      newSlides[targetIndex],
      newSlides[index],
    ];

    // Optimistic update
    setSlides(newSlides);

    try {
      const slideIds = newSlides.map((s) => s.id);
      await reorderCarouselSlides(slideIds);
      // Wait for reorder to finish then fetch to ensure complete sync
      fetchSlides();
    } catch (error) {
      console.error("Failed to reorder slides:", error);
      alert("Failed to reorder slides. They may be out of sync.");
      fetchSlides(); // Revert back on error
    }
  };

  if (isFormOpen) {
    return (
      <AdminPageShell className="max-w-4xl">
        <AdminBackButton
          onClick={() => {
            setIsFormOpen(false);
            setEditingSlide(undefined);
          }}
          label="Back to Carousel List"
        />
        <CarouselSlideForm
          initialData={editingSlide}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingSlide(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Carousel Management"
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingSlide(undefined);
              setIsFormOpen(true);
            }}
          >
            Create Slide
          </Button>
        }
      />

      <AdminCard>
        {isLoading ? (
          <div className="py-20 text-center text-slate-500">
            Loading data...
          </div>
        ) : slides.length === 0 ? (
          <div className="py-10 text-center text-slate-500">
            No records found. Create one.
          </div>
        ) : (
          <div className="space-y-4">
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                className="flex items-center border border-gray-200 rounded-lg p-4 bg-gray-50 flex-col sm:flex-row gap-4"
              >
                {/* Reorder Buttons */}
                <div className="flex flex-col gap-1 items-center justify-center -ml-2 p-2">
                  <button
                    disabled={index === 0}
                    onClick={() => moveSlide(index, "up")}
                    className={`p-1 rounded bg-white border ${index === 0 ? "text-gray-300 border-gray-100" : "text-gray-700 border-gray-300 hover:bg-gray-100"}`}
                    title="Move Up"
                  >
                    ↑
                  </button>
                  <button
                    disabled={index === slides.length - 1}
                    onClick={() => moveSlide(index, "down")}
                    className={`p-1 rounded bg-white border ${index === slides.length - 1 ? "text-gray-300 border-gray-100" : "text-gray-700 border-gray-300 hover:bg-gray-100"}`}
                    title="Move Down"
                  >
                    ↓
                  </button>
                </div>

                {/* Preview Image */}
                <div className="w-48 h-28 relative bg-gray-200 rounded overflow-hidden flex-shrink-0">
                  <Image
                    src={
                      failedImageIds[slide.id]
                        ? IMAGE_ERROR_FALLBACK_SRC
                        : slide.image_url
                    }
                    alt={slide.overlay_text || "Carousel slide"}
                    className="object-cover"
                    fill
                    unoptimized
                    sizes="192px"
                    onError={() =>
                      setFailedImageIds((prev) => ({
                        ...prev,
                        [slide.id]: true,
                      }))
                    }
                  />
                </div>

                {/* Slide Details */}
                <div className="flex-grow">
                  <h3 className="font-bold text-lg mb-1">
                    {slide.overlay_text || (
                      <span className="text-gray-400 italic">
                        No overlay text
                      </span>
                    )}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2 truncate max-w-md">
                    <span className="font-semibold">Link:</span>{" "}
                    {slide.link_url || "None"}
                  </p>
                  <span
                    className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                      slide.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-slate-100 text-slate-700"
                    }`}
                  >
                    {slide.is_active ? "Active" : "Inactive"}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex sm:flex-col gap-3 sm:ml-auto">
                  <Button
                    onClick={() => handleEdit(slide)}
                    type="button"
                    variant="outline"
                    size="sm"
                    className="whitespace-nowrap"
                  >
                    Edit
                  </Button>
                  <Button
                    onClick={() => handleDelete(slide.id)}
                    type="button"
                    variant="destructive"
                    size="sm"
                    className="whitespace-nowrap"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </AdminCard>
    </AdminPageShell>
  );
}
