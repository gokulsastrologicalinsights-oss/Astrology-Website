import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { PropertyNumerologyStudio } from "@/components/numerology/PropertyNumerologyStudio";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Property & House Numerology Studio | Gokul's Astrological Insights",
  description:
    "Analyze independent villas, apartment flats, commercial offices, and land plots across 6 distinct numerological calculation modes, evaluate 8-direction classical Vastu orientations, and align with multi-resident family astrology.",
};

export default function PropertyStudioPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Navigation Breadcrumbs */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <Breadcrumbs
          items={[
            {
              label: "Astrology Tools",
              href: "/tools",
            },
            {
              label: "Numerology",
              href: "/tools/numerology",
            },
            {
              label: "Property & House Studio",
            },
          ]}
        />

        <Link
          href="/tools/numerology"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Numerology Hub</span>
        </Link>
      </div>

      <PropertyNumerologyStudio />
    </div>
  );
}
