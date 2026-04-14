"use client";

import { CarouselSlideForm } from "@/components/admin/CarouselSlideForm";
import { CarouselSlide } from "@/types";
import { CreateCarouselSlide } from "@/types/admin";
import {
  createCarouselSlide,
  deleteCarouselSlide,
  getAdminCarouselSlides,
  updateCarouselSlide,
  reorderCarouselSlides,
} from "@/lib/admin-api";
import { useEffect, useState } from "react";

export default function AdminCarouselPage() {
  const [slides, setSlides] = useState<CarouselSlide[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSlide, setEditingSlide] = useState<CarouselSlide | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);

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
        formData.display_order = slides.length > 0 
          ? Math.max(...slides.map(s => s.display_order)) + 1
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
      <div className="max-w-4xl mx-auto space-y-4">
        <button
          onClick={() => {
            setIsFormOpen(false);
            setEditingSlide(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Carousel List
        </button>
        <CarouselSlideForm
          initialData={editingSlide}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingSlide(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Carousel Management</h1>
        <button
          onClick={() => {
            setEditingSlide(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Create Slide
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">Loading slides...</div>
        ) : slides.length === 0 ? (
          <div className="text-center py-10 text-gray-500">
            No slides found. Create one!
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
                  <img
                    src={slide.image_url}
                    alt={slide.overlay_text || "Carousel slide"}
                    className="object-cover w-full h-full"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='%23e5e7eb'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='12px' fill='%239ca3af'%3EError loading image%3C/text%3E%3C/svg%3E";
                    }}
                  />
                </div>

                {/* Slide Details */}
                <div className="flex-grow">
                  <h3 className="font-bold text-lg mb-1">
                    {slide.overlay_text || <span className="text-gray-400 italic">No overlay text</span>}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2 truncate max-w-md">
                    <span className="font-semibold">Link:</span> {slide.link_url || "None"}
                  </p>
                  <span
                    className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                      slide.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-gray-200 text-gray-800"
                    }`}
                  >
                    {slide.is_active ? "Active" : "Inactive"}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex sm:flex-col gap-3 sm:ml-auto">
                  <button
                    onClick={() => handleEdit(slide)}
                    className="text-blue-600 hover:text-blue-900 font-medium whitespace-nowrap bg-white px-3 py-1.5 border rounded shadow-sm"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(slide.id)}
                    className="text-red-600 hover:text-red-900 font-medium whitespace-nowrap bg-white px-3 py-1.5 border border-red-200 rounded shadow-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
