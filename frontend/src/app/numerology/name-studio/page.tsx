import React from "react";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { NameCorrectionStudio } from "@/components/numerology/NameCorrectionStudio";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Name Suggestion & Correction Studio | Gokul's Astrological Insights",
  description: "Deterministic name vibration analysis, phonetic preservation scoring, and spelling correction under Pythagorean and Chaldean traditions.",
};

export default function NameStudioPage() {
  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
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
              label: "Name Suggestion & Correction Studio",
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
      <NameCorrectionStudio />
    </div>
  );
}
