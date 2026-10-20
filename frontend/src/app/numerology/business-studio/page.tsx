import React from "react";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { BusinessNumerologyStudio } from "@/components/numerology/BusinessNumerologyStudio";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Business & Brand Numerology Studio | Gokul's Astrological Insights",
  description: "Corporate legal entity vs public brand normalization, multi-founder equity harmony matrix, tagline synergy, and industry vibrational audit.",
};

export default function BusinessStudioPage() {
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
              label: "Business & Brand Studio",
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

      {/* Main Studio View */}
      <BusinessNumerologyStudio />
    </div>
  );
}
