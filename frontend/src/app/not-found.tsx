"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Compass, ArrowLeft } from "lucide-react";

export default function NotFound() {
  const { language, t } = useLanguage();

  useEffect(() => {
    document.title = `404 — ${language === "ta" ? "பக்கம் கிடைக்கவில்லை" : "Page Not Found"} | ${t.brandName}`;
  }, [language, t.brandName]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-16">
      <div className="max-w-md w-full text-center space-y-6 bg-white p-8 rounded-xl border border-[#E2DCD5] shadow-xs">
        <div className="w-16 h-16 rounded-full bg-[#FAF2DE] border border-[#D8BD80] flex items-center justify-center mx-auto text-[#B8860B]">
          <Compass className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <span className="text-[11px] font-mono uppercase tracking-wider text-[#8C6D23] font-semibold">
            {t.brandName}
          </span>
          <h1 className="font-serif text-3xl font-bold text-[#0F172A]">404</h1>
          <h2 className="font-serif text-lg font-bold text-[#0F172A]">
            {language === "ta" ? "பக்கம் கிடைக்கவில்லை" : "Page Not Found"}
          </h2>
          <p className="text-xs sm:text-sm text-[#64748B] leading-relaxed">
            {language === "ta"
              ? "நீங்கள் தேடும் பக்கம் நகர்த்தப்பட்டிருக்கலாம் அல்லது கிடைக்காமல் போயிருக்கலாம்."
              : "The astrological resource or page you requested could not be found."}
          </p>
        </div>
        <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            href="/"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold text-white bg-[#0F172A] hover:bg-[#1E293B] shadow-xs transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{t.navHome}</span>
          </Link>
          <Link
            href="/horoscope"
            className="w-full sm:w-auto inline-flex items-center justify-center px-5 py-2.5 rounded-lg text-xs font-semibold text-[#0F172A] bg-[#FAF2DE] border border-[#D8BD80] hover:bg-[#FAF6EC] shadow-2xs transition-colors"
          >
            {t.navHoroscope}
          </Link>
        </div>
      </div>
    </div>
  );
}
