"use client";

import { IMAGE_PATHS } from "@/lib/imagePaths";
import type { CarouselSlide } from "@/types";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

interface CarouselProps {
  slides: CarouselSlide[];
}

const fallbackSlides: CarouselSlide[] = [
  {
    id: -1,
    image_url: IMAGE_PATHS.carouselFrontFallbacks[0],
    overlay_text: "Welcome to the UNC Undergraduate Senate",
    link_url: "/about/powers",
    display_order: 0,
    is_active: true,
  },
  {
    id: -2,
    image_url: IMAGE_PATHS.carouselFrontFallbacks[1],
    overlay_text: "Track legislation, meetings, and resources",
    link_url: "/legislation/search",
    display_order: 1,
    is_active: true,
  },
  {
    id: -3,
    image_url: IMAGE_PATHS.carouselFrontFallbacks[2],
    overlay_text: "Stay current with senate updates",
    link_url: "/news",
    display_order: 2,
    is_active: true,
  },
];

function isExternalUrl(url: string): boolean {
  return /^https?:\/\//i.test(url);
}

export default function Carousel({ slides }: CarouselProps) {
  const activeSlides = useMemo(() => {
    const filteredSlides = slides
      .filter((slide) => slide.is_active)
      .sort((a, b) => a.display_order - b.display_order);

    if (filteredSlides.length > 0) {
      return filteredSlides;
    }

    return fallbackSlides;
  }, [slides]);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const slideCount = activeSlides.length;

  useEffect(() => {
    if (slideCount <= 1 || isPaused) {
      return;
    }

    const timer = setInterval(() => {
      setCurrentIndex((previousIndex) => (previousIndex + 1) % slideCount);
    }, 5000);

    return () => clearInterval(timer);
  }, [slideCount, isPaused]);

  useEffect(() => {
    if (currentIndex >= slideCount && slideCount > 0) {
      setCurrentIndex(0);
    }
  }, [currentIndex, slideCount]);

  const goToPrevious = () => {
    setCurrentIndex((previousIndex) =>
      previousIndex === 0 ? slideCount - 1 : previousIndex - 1,
    );
  };

  const goToNext = () => {
    setCurrentIndex((previousIndex) => (previousIndex + 1) % slideCount);
  };

  return (
    <section
      className="relative w-full overflow-hidden bg-gray-900"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
      aria-label="Homepage carousel"
    >
      <div className="relative aspect-[21/9] min-h-[260px] w-full">
        <div
          className="flex h-full transition-transform duration-700 ease-out"
          style={{ transform: `translateX(-${currentIndex * 100}%)` }}
        >
          {activeSlides.map((slide, index) => {
            const slideContent = (
              <>
                <Image
                  src={slide.image_url || IMAGE_PATHS.carouselFallback}
                  alt={slide.overlay_text || "Homepage carousel slide"}
                  fill
                  className="object-cover"
                  sizes="100vw"
                  priority={index === 0}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                {slide.overlay_text ? (
                  <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8">
                    <p className="max-w-4xl text-lg font-semibold text-white sm:text-2xl">
                      {slide.overlay_text}
                    </p>
                  </div>
                ) : null}
              </>
            );

            return (
              <div key={slide.id} className="relative h-full min-w-full">
                {slide.link_url ? (
                  isExternalUrl(slide.link_url) ? (
                    <a
                      href={slide.link_url}
                      target="_blank"
                      rel="noreferrer"
                      className="absolute inset-0 block"
                      aria-label={slide.overlay_text || "Carousel slide link"}
                    >
                      {slideContent}
                    </a>
                  ) : (
                    <Link
                      href={slide.link_url}
                      className="absolute inset-0 block"
                      aria-label={slide.overlay_text || "Carousel slide link"}
                    >
                      {slideContent}
                    </Link>
                  )
                ) : (
                  <div className="absolute inset-0">{slideContent}</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {slideCount > 1 ? (
        <>
          <button
            type="button"
            onClick={goToPrevious}
            className="absolute left-3 top-1/2 z-10 -translate-y-1/2 rounded-full bg-black/45 px-3 py-2 text-xl text-white transition hover:bg-black/65"
            aria-label="Previous slide"
          >
            &lt;
          </button>
          <button
            type="button"
            onClick={goToNext}
            className="absolute right-3 top-1/2 z-10 -translate-y-1/2 rounded-full bg-black/45 px-3 py-2 text-xl text-white transition hover:bg-black/65"
            aria-label="Next slide"
          >
            &gt;
          </button>

          <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 gap-2">
            {activeSlides.map((slide, index) => (
              <button
                key={slide.id}
                type="button"
                onClick={() => setCurrentIndex(index)}
                className={`h-2.5 w-2.5 rounded-full transition ${
                  index === currentIndex
                    ? "bg-white"
                    : "bg-white/45 hover:bg-white/70"
                }`}
                aria-label={`Go to slide ${index + 1}`}
                aria-current={index === currentIndex ? "true" : undefined}
              />
            ))}
          </div>
        </>
      ) : null}
    </section>
  );
}
