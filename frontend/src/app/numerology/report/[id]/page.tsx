import React, { Suspense, use } from "react";
import { Loader2 } from "lucide-react";
import ReportClient from "./ReportClient";

interface PageProps {
  params: Promise<{ id: string }>;
}

function ReportLoader({ params }: PageProps) {
  const { id } = use(params);
  return <ReportClient reportId={id} />;
}

export default function SavedReportDetailPage({ params }: PageProps) {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <Loader2 className="w-8 h-8 mx-auto animate-spin text-[#B8860B] mb-3" />
          <p className="text-sm text-[#64748B]">Loading saved report...</p>
        </div>
      }
    >
      <ReportLoader params={params} />
    </Suspense>
  );
}
