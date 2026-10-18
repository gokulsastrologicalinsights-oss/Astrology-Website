"use client";

import { Suspense } from "react";
import { NumerologySectionView } from "@/components/numerology/NumerologySectionView";

export default function NumerologyLandingPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#E8EEF7]">
          <div className="w-8 h-8 border-4 border-[#3478F6] border-t-transparent rounded-full animate-spin" />
        </div>
      }
    >
      <NumerologySectionView />
    </Suspense>
  );
}
