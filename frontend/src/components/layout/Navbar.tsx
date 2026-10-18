"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { getHealth } from "@/lib/api";
import { HealthResponse } from "@/lib/types";
import { HeaderSearch } from "./HeaderSearch";
import { HelpModal } from "./HelpModal";
import {
  Globe,
  Menu,
  X,
  Compass,
  Activity,
  User as UserIcon,
  LogOut,
  Shield,
  LayoutDashboard,
  LogIn,
  HelpCircle,
  Sparkles,
  Home as HomeIcon,
  ChevronDown,
  Calendar,
} from "lucide-react";

export function Navbar() {
  const pathname = usePathname();
  const { language, toggleLanguage, t } = useLanguage();
  const { user, role, isAuthenticated, isLoading, logout } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);

  useEffect(() => {
    let isMounted = true;
    getHealth()
      .then((res) => {
        if (isMounted) setHealth(res);
      })
      .catch(() => {
        if (isMounted) setHealth(null);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const isLoginPage =
    pathname === "/login" ||
    pathname === "/forgot-password" ||
    pathname === "/register" ||
    pathname === "/update-password";

  // Exactly THREE primary navigation items when authenticated
  const mainNavItems = [
    {
      href: "/",
      label: t.navHome || "Home",
      icon: HomeIcon,
      isActive: pathname === "/" || pathname === "/home",
    },
    {
      href: "/dashboard",
      label: t.navDashboard || "Dashboard",
      icon: LayoutDashboard,
      isActive: pathname === "/dashboard" || pathname.startsWith("/admin"),
    },
    {
      href: "/tools",
      label: t.navTools || "Astrology Tools",
      icon: Sparkles,
      isActive:
        pathname.startsWith("/tools") ||
        pathname.startsWith("/horoscope") ||
        pathname.startsWith("/numerology"),
    },
    {
      href: "/muhurta",
      label: t.navMuhurta || "Muhurta",
      icon: Calendar,
      isActive: pathname.startsWith("/muhurta"),
    },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 w-full bg-white border-b border-[#DDE5F0] shadow-xs">
        {/* Top Header Row */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-16 flex items-center justify-between gap-3 sm:gap-6">
            {/* 1. Brand Logo & Name */}
            <Link
              href={isAuthenticated ? "/" : "/login"}
              className="flex items-center gap-3 shrink-0 group focus:outline-hidden"
              aria-label="Gokul’s Astrological Insights Home"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#102A4C] via-[#1E3A61] to-[#3478F6] flex items-center justify-center text-white shadow-xs border border-[#3478F6]/30 group-hover:scale-105 transition-transform">
                <Compass className="w-5 h-5 text-[#FAF2DE] transition-transform group-hover:rotate-45" />
              </div>
              <div className="min-w-0">
                <div className="font-serif text-base sm:text-lg font-bold text-[#102A4C] tracking-tight leading-tight truncate">
                  {t.brandName}
                </div>
                <div className="text-[10px] sm:text-[11px] text-[#52667E] truncate hidden sm:block">
                  {language === "ta"
                    ? "துல்லிய வேத & கே.பி வானியல் தளம்"
                    : "Precision Vedic & KP Astronomical System"}
                </div>
              </div>
            </Link>

            {/* 2. Center Search Bar (for authenticated users) */}
            {isAuthenticated && !isLoginPage && (
              <div className="hidden lg:flex flex-1 justify-center max-w-md mx-2">
                <HeaderSearch />
              </div>
            )}

            {/* 3. Primary Desktop Navigation Tabs (Only 3 Items) */}
            {isAuthenticated && !isLoginPage && (
              <nav
                className="hidden md:flex items-center gap-1 bg-[#F8FAFC] p-1 rounded-xl border border-[#DDE5F0]"
                aria-label="Primary Navigation"
              >
                {mainNavItems.map((item) => {
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        item.isActive
                          ? "bg-white text-[#102A4C] shadow-2xs border border-[#DDE5F0]"
                          : "text-[#52667E] hover:text-[#102A4C] hover:bg-white/60"
                      }`}
                    >
                      <Icon
                        className={`w-3.5 h-3.5 ${
                          item.isActive ? "text-[#3478F6]" : "text-[#94A3B8]"
                        }`}
                      />
                      <span>{item.label}</span>
                    </Link>
                  );
                })}
              </nav>
            )}

            {/* 4. Controls: Health, Language, Help, Profile & Mobile Toggle */}
            <div className="flex items-center gap-2 sm:gap-2.5 shrink-0">
              {/* Engine Health Indicator */}
              <div
                className="hidden xl:flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border border-[#DDE5F0] bg-[#F8FAFC]"
                title={
                  health?.status === "healthy"
                    ? `${health.engine.name} (${health.engine.version}) Ready`
                    : "Checking backend connection..."
                }
              >
                <Activity
                  className={`w-3 h-3 ${
                    health?.status === "healthy"
                      ? "text-emerald-500 animate-pulse"
                      : "text-amber-500"
                  }`}
                />
                <span className="text-[#52667E] font-medium text-[11px]">
                  {health?.status === "healthy" ? t.statusOnline : t.statusOffline}
                </span>
              </div>

              {/* Language Switcher */}
              <button
                type="button"
                onClick={toggleLanguage}
                className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-white hover:bg-[#F8FAFC] text-xs font-semibold text-[#102A4C] transition-all cursor-pointer shadow-2xs"
                aria-label="Toggle language"
              >
                <Globe className="w-3.5 h-3.5 text-[#3478F6]" />
                <span className="text-xs">{language === "en" ? "தமிழ்" : "English"}</span>
              </button>

              {/* Help & Support Button */}
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={() => setIsHelpOpen(true)}
                  className="p-1.5 sm:px-2.5 sm:py-1.5 rounded-xl border border-[#DDE5F0] bg-white hover:bg-[#F8FAFC] text-xs font-semibold text-[#52667E] hover:text-[#102A4C] transition-all cursor-pointer shadow-2xs inline-flex items-center gap-1"
                  aria-label="Open Platform Guide and Help"
                  title={t.helpGuide || "Help & Guide"}
                >
                  <HelpCircle className="w-4 h-4 text-[#3478F6]" />
                  <span className="hidden sm:inline">{t.helpGuide || "Help"}</span>
                </button>
              )}

              {/* Auth Profile Controls */}
              {!isLoading && (
                <>
                  {isAuthenticated && user ? (
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                        className="flex items-center gap-2 px-2.5 sm:px-3 py-1.5 rounded-xl border border-[#DDE5F0] bg-[#F8FAFC] hover:bg-[#EFF6FF] text-xs font-semibold text-[#102A4C] shadow-2xs transition-all cursor-pointer"
                        aria-expanded={userDropdownOpen}
                        aria-label="User profile menu"
                      >
                        <div className="w-5 h-5 rounded-full bg-[#102A4C] text-white flex items-center justify-center text-[10px] font-bold">
                          {user.username?.charAt(0).toUpperCase() || "U"}
                        </div>
                        <span className="max-w-[80px] sm:max-w-[110px] truncate hidden sm:inline">
                          {user.displayName || user.username}
                        </span>
                        {user.role === "admin" && (
                          <span className="px-1.5 py-0.2 rounded text-[9px] font-bold uppercase bg-[#B8862B] text-white hidden md:inline">
                            Admin
                          </span>
                        )}
                        <ChevronDown className="w-3.5 h-3.5 text-[#64748B]" />
                      </button>

                      {userDropdownOpen && (
                        <div
                          className="absolute right-0 mt-2 w-56 rounded-2xl shadow-xl bg-white border border-[#DDE5F0] py-2 z-50 divide-y divide-[#F1F5F9] animate-in fade-in duration-150"
                          onMouseLeave={() => setUserDropdownOpen(false)}
                        >
                          <div className="px-4 py-2.5 text-xs">
                            <div className="font-bold text-[#102A4C] truncate">
                              {user.displayName || user.username}
                            </div>
                            <div className="truncate text-[11px] text-[#64748B]">
                              {user.email || `@${user.username}`}
                            </div>
                            <div className="mt-1 flex items-center gap-1.5">
                              <span className="inline-flex items-center gap-1 px-2 py-0.2 rounded text-[10px] font-semibold bg-[#EBF2FE] text-[#3478F6] border border-[#BFDBFE]">
                                <Shield className="w-2.5 h-2.5" />
                                {user.role === "admin" ? "Administrator" : "Standard User"}
                              </span>
                            </div>
                          </div>

                          <div className="py-1">
                            <Link
                              href="/"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <HomeIcon className="w-3.5 h-3.5 text-[#3478F6]" />
                              <span>{t.navHome || "Home"}</span>
                            </Link>

                            <Link
                              href="/dashboard"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <LayoutDashboard className="w-3.5 h-3.5 text-[#3478F6]" />
                              <span>{t.navDashboard || "Dashboard"}</span>
                            </Link>

                            <Link
                              href="/horoscopes"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                              <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
                            </Link>

                            <Link
                              href="/tools"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <Sparkles className="w-3.5 h-3.5 text-[#B8862B]" />
                              <span>{t.navTools || "Astrology Tools"}</span>
                            </Link>

                            <Link
                              href="/vastu"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#334155] hover:bg-[#F8FAFC] transition-colors"
                            >
                              <HomeIcon className="w-3.5 h-3.5 text-blue-600" />
                              <span>{language === "ta" ? "வாஸ்து சாஸ்திரம்" : "Vastu Shastra"}</span>
                            </Link>

                            {user.role === "admin" && (
                              <Link
                                href="/admin"
                                onClick={() => setUserDropdownOpen(false)}
                                className="flex items-center gap-2.5 px-4 py-2 text-xs text-amber-700 hover:bg-amber-50 transition-colors"
                              >
                                <Shield className="w-3.5 h-3.5 text-amber-600" />
                                <span>{t.navAdmin || "Admin Portal"}</span>
                              </Link>
                            )}
                          </div>

                          <div className="pt-1">
                            <button
                              type="button"
                              onClick={() => {
                                setUserDropdownOpen(false);
                                logout();
                              }}
                              className="w-full flex items-center gap-2 px-4 py-2 text-xs text-rose-600 hover:bg-rose-50 text-left transition-colors cursor-pointer"
                            >
                              <LogOut className="w-3.5 h-3.5" />
                              <span>{t.navLogout}</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    !isLoginPage && (
                      <Link
                        href="/login"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[#102A4C] bg-[#102A4C] hover:bg-[#1E3A61] text-xs font-semibold text-white shadow-xs transition-colors"
                      >
                        <LogIn className="w-3.5 h-3.5" />
                        <span>{t.navLogin}</span>
                      </Link>
                    )
                  )}
                </>
              )}

              {/* Mobile Menu Toggle Button */}
              {isAuthenticated && !isLoginPage && (
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="md:hidden p-2 rounded-xl text-[#334155] hover:text-[#102A4C] hover:bg-[#F8FAFC] border border-[#DDE5F0]"
                  aria-label="Open mobile navigation menu"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#DDE5F0] bg-white px-4 pt-3 pb-5 space-y-4 shadow-lg animate-in slide-in-from-top-2 duration-150">
            {/* Mobile Search */}
            <div className="pt-1">
              <HeaderSearch />
            </div>

            {/* Mobile 3-Item Navigation */}
            <nav className="flex flex-col space-y-1" aria-label="Mobile Navigation">
              {mainNavItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold ${
                      item.isActive
                        ? "bg-[#EBF2FE] text-[#3478F6]"
                        : "text-[#334155] hover:bg-[#F8FAFC]"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Mobile Profile & Logout */}
            <div className="pt-3 border-t border-[#DDE5F0] space-y-2">
              {isAuthenticated && user && (
                <div className="flex items-center justify-between py-1">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-[#102A4C] text-white flex items-center justify-center text-xs font-bold">
                      {user.username?.charAt(0).toUpperCase() || "U"}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-[#102A4C]">
                        {user.displayName || user.username}
                      </div>
                      <div className="text-[10px] text-[#64748B]">@{user.username}</div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setMobileMenuOpen(false);
                      logout();
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold text-rose-600 hover:bg-rose-50 cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>{t.navLogout}</span>
                  </button>
                </div>
              )}

              {isAuthenticated && (
                <div className="pt-1 flex flex-col space-y-1">
                  <Link
                    href="/horoscopes"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#334155] hover:bg-[#F8FAFC]"
                  >
                    <Compass className="w-3.5 h-3.5 text-[#B8862B]" />
                    <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
                  </Link>

                  <Link
                    href="/vastu"
                    onClick={() => setMobileMenuOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-[#334155] hover:bg-[#F8FAFC]"
                  >
                    <HomeIcon className="w-3.5 h-3.5 text-blue-600" />
                    <span>{language === "ta" ? "வாஸ்து சாஸ்திரம்" : "Vastu Shastra"}</span>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </header>

      {/* Guide & Help Modal */}
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
    </>
  );
}
