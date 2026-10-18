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

export default function SavedVastuReportDetailPage({ params }: PageProps) {
  return (
    <Suspense
      fallback={
        <div className="max-w-4xl mx-auto px-4 py-20 text-center">
          <Loader2 className="w-8 h-8 mx-auto animate-spin text-blue-600 mb-3" />
          <p className="text-sm text-slate-500">Loading saved Vastu assessment...</p>
        </div>
      }
    >
      <ReportLoader params={params} />
    </Suspense>
  );
}
