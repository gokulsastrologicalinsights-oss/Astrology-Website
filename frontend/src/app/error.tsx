"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { AlertCircle, RotateCcw, ArrowLeft } from "lucide-react";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { language, t } = useLanguage();

  useEffect(() => {
    console.error("Runtime application error:", error);
    document.title = `${t.error} | ${t.brandName}`;
  }, [error, t.error, t.brandName]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-16">
      <div className="max-w-md w-full text-center space-y-6 bg-white p-8 rounded-xl border border-rose-200 shadow-xs">
        <div className="w-16 h-16 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center mx-auto text-rose-600">
          <AlertCircle className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <span className="text-[11px] font-mono uppercase tracking-wider text-[#8C6D23] font-semibold">
            {t.brandName}
          </span>
          <h1 className="font-serif text-2xl font-bold text-[#0F172A]">{t.error}</h1>
          <p className="text-xs sm:text-sm text-[#64748B] leading-relaxed">
            {language === "ta"
              ? "ஒரு எதிர்பாராத பிழை ஏற்பட்டது. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
              : "An unexpected error occurred while processing calculations."}
          </p>
          {error.digest && (
            <p className="text-[10px] font-mono text-[#94A3B8]">
              Digest: {error.digest}
            </p>
          )}
        </div>
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            type="button"
            onClick={() => reset()}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>{t.retry}</span>
          </button>
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-xs font-semibold text-[#0F172A] bg-[#FAF2DE] border border-[#D8BD80] hover:bg-[#FAF6EC] shadow-2xs transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{t.navHome}</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
