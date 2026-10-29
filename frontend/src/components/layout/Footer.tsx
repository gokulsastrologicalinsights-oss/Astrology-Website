"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { Compass, ShieldCheck } from "lucide-react";

export function Footer() {
  const pathname = usePathname();
  const { language, t } = useLanguage();
  const isLoginPage = pathname === "/login" || pathname === "/forgot-password" || pathname === "/register";

  return (
    <footer className="w-full border-t border-[#DDE5F0] bg-white text-[#52667E] mt-auto">
      <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand & Mission */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-[#102A4C] flex items-center justify-center text-white">
                <Compass className="w-4 h-4 text-[#B8862B]" />
              </div>
              <span className="font-serif text-lg font-bold text-[#102A4C]">
                {t.brandName}
              </span>
            </div>
            <p className="text-xs text-[#52667E] leading-relaxed max-w-md">
              {t.heroSubtitle}
            </p>
            <div className="flex items-center gap-2 text-[11px] text-[#3478F6] font-medium pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{t.footerEngineInfo}</span>
            </div>
          </div>

          {/* Quick Links (Hidden on Login Screen) */}
          {!isLoginPage ? (
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider text-[#102A4C] mb-3">
                {language === "ta" ? "முக்கிய வழிகாட்டல்" : "Application Navigation"}
              </h5>
              <ul className="space-y-2 text-xs">
                <li>
                  <Link href="/" className="hover:text-[#3478F6] transition-colors">
                    {t.navHome || "Home"}
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-[#3478F6] transition-colors">
                    {t.navDashboard}
                  </Link>
                </li>
                <li>
                  <Link href="/tools" className="hover:text-[#3478F6] transition-colors">
                    {t.navTools || "Astrology Tools"}
                  </Link>
                </li>
                <li>
                  <Link href="/tools/horoscope" className="hover:text-[#3478F6] transition-colors">
                    Horoscope / KP System
                  </Link>
                </li>
                <li>
                  <Link href="/tools/numerology" className="hover:text-[#3478F6] transition-colors">
                    Numerology
                  </Link>
                </li>
              </ul>
            </div>
          ) : (
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider text-[#0F172A] mb-3">
                {language === "ta" ? "அணுகல் பாதுகாப்பு" : "Access Security"}
              </h5>
              <p className="text-xs text-[#64748B] leading-relaxed">
                {language === "ta"
                  ? "அங்கீகரிக்கப்பட்ட பயனர்களுக்கு மட்டுமே அனுமதி. உள்நுழைவு அவசியம்."
                  : "Authenticated access only. Sign in required to enter the application portal."}
              </p>
            </div>
          )}

          {/* Systems Supported */}
          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-[#0F172A] mb-3">
              {language === "ta" ? "கணித முறைகள்" : "Supported Canons"}
            </h5>
            <ul className="space-y-2 text-xs text-[#64748B]">
              <li>{language === "ta" ? "சித்ரபக்ஷ லஹரி அயனாம்சம்" : "Lahiri (Chitrapaksha) Sidereal"}</li>
              <li>{language === "ta" ? "கே.பி கிருஷ்ணமூர்த்தி பத்தாதி (249)" : "KP Krishnamurti Paddhati (249)"}</li>
              <li>{language === "ta" ? "விம்சோத்தரி தசை (365.25 நாள்/ஆண்டு)" : "Vimshottari Dasa (365.25d)"}</li>
              <li>{language === "ta" ? "தென்/வடஇந்திய கட்ட அமைப்புகள்" : "South & North Indian Charts"}</li>
            </ul>
          </div>
        </div>

        {/* Methodology & Legal Disclaimer Notice */}
        <div className="mt-8 pt-6 border-t border-[#E8DEC8]/80 text-[11px] text-[#64748B] space-y-2">
          <p className="leading-relaxed">
            <strong className="text-[#0F172A]">
              {language === "ta" ? "முக்கிய அறிவிப்பு" : "Methodology Disclaimer"}:
            </strong>{" "}
            {t.footerDisclaimer}
          </p>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pt-2 text-[#94A3B8]">
            <div>{t.footerCopyright} • Geocoding © OpenStreetMap contributors</div>
            <div className="font-mono text-[10px]">Deterministic Engine • Zero AI Assumptions</div>
          </div>
        </div>
      </div>
    </footer>
  );
}
