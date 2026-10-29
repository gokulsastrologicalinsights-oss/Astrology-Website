import React from "react";
import Link from "next/link";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { PhoneNumberStudio } from "@/components/numerology/PhoneNumberStudio";
import { ArrowLeft } from "lucide-react";

export const metadata = {
  title: "Phone & Mobile Number Numerology Analyzer | Gokul's Astrological Insights",
  description: "Deterministic SIM card and phone number numerology, digit frequency distribution, missing vibrations, VIP vanity scoring, and personal/business resonance.",
};

export default function PhoneStudioPage() {
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
              label: "Phone & Mobile Studio",
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
      <PhoneNumberStudio />
    </div>
  );
}
