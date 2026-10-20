import type { Metadata } from "next";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { VehicleNumberStudio } from "@/components/numerology/VehicleNumberStudio";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Vehicle Registration Numerology Studio | Gokul's Astrological Insights",
  description:
    "Analyze motor vehicle registration plates (TN, MH, DL, KA, BH series) across numeric and full alphanumeric traditions, evaluate VIP vanity patterns, and align with owner astrology.",
};

export default function VehicleStudioPage() {
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
              label: "Vehicle Registration Studio",
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

      <VehicleNumberStudio />
    </div>
  );
}
