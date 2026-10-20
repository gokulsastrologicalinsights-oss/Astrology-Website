"use client";

import React, { useEffect, useState, useRef } from "react";
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
  LogOut,
  Shield,
  LayoutDashboard,
  LogIn,
  Sparkles,
  Home as HomeIcon,
  ChevronDown,
  Calendar,
  Cake,
  Flame,
  Briefcase,
  BookOpen,
  GraduationCap,
  Layers,
  Clock,
  Headphones,
  Settings,
  Database,
  User,
  Home,
  Heart,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";

export function Navbar() {
  const pathname = usePathname();
  const { language, toggleLanguage, t } = useLanguage();
  const { user, role, isAuthenticated, isLoading, logout } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isBirthdayOpen, setIsBirthdayOpen] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);

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

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setActiveDropdown(null);
        setUserDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close menus on path change
  useEffect(() => {
    setActiveDropdown(null);
    setUserDropdownOpen(false);
    setMobileMenuOpen(false);
  }, [pathname]);

  const isLoginPage =
    pathname === "/login" ||
    pathname === "/forgot-password" ||
    pathname === "/register" ||
    pathname === "/update-password";

  // Navigation Items with Submenus matching reference screenshots
  const navItems = [
    {
      id: "home",
      label: language === "ta" ? "முகப்பு" : "Home",
      icon: HomeIcon,
      href: "/",
      isActive: pathname === "/" || pathname === "/home",
      hasDropdown: false,
    },
    {
      id: "tools",
      label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
      icon: Layers,
      href: "/tools",
      isActive:
        pathname.startsWith("/tools") ||
        pathname.startsWith("/horoscope") ||
        pathname.startsWith("/numerology") ||
        pathname.startsWith("/muhurta") ||
        pathname.startsWith("/vastu") ||
        pathname.startsWith("/remedies"),
      hasDropdown: true,
      children: [
        {
          title: language === "ta" ? "ஜாதகம் (வேத & கே.பி)" : "Horoscope (Vedic & KP)",
          href: "/tools/horoscope",
          icon: Compass,
        },
        {
          title: language === "ta" ? "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு" : "Horoscope Writing",
          href: "/tools/horoscope-writing",
          icon: BookOpen,
        },
        {
          title: language === "ta" ? "உயர்நிலை கே.பி. முறை" : "Advanced KP System",
          href: "/tools/advanced-kp",
          icon: Layers,
        },
        {
          title: language === "ta" ? "கோச்சார ஜாதகம்" : "KP Transit Watch",
          href: "/tools/transit-watch",
          icon: Clock,
        },
        {
          title: language === "ta" ? "கே.பி. நிகழ்வு கணிப்பு" : "KP Events & Prediction",
          href: "/tools/kp-events-prediction",
          icon: Sparkles,
        },
        {
          title: language === "ta" ? "திருமண கணிப்பு" : "Marriage Prediction",
          href: "/tools/marriage-prediction",
          icon: Heart,
        },
        {
          title: language === "ta" ? "D1 ராசி & D9 நவாம்சம்" : "D1 Rasi & D9 Navamsa",
          href: "/tools/d1-d9",
          icon: Compass,
        },
        {
          title: language === "ta" ? "எண் கணிதம்" : "Numerology System",
          href: "/tools/numerology",
          icon: Sparkles,
        },
        {
          title: language === "ta" ? "தினசரி பஞ்சாங்கம் & முகூர்த்தம்" : "Daily Panchang & Muhurta",
          href: "/muhurta",
          icon: Calendar,
        },
        {
          title: language === "ta" ? "வாஸ்து சாஸ்திரம்" : "Vastu Shastra Assessment",
          href: "/vastu",
          icon: Home,
        },
        {
          title: language === "ta" ? "பரிகாரங்கள் & நவகிரக ஆலயங்கள்" : "Remedies & Pariharam Hub",
          href: "/remedies",
          icon: Flame,
        },
      ],
    },
    {
      id: "workspace",
      label: language === "ta" ? "என் பயிற்சி" : "My Practice",
      icon: Briefcase,
      href: "/horoscopes",
      isActive: pathname === "/horoscopes",
      hasDropdown: true,
      children: [
        {
          title: language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes Directory",
          href: "/horoscopes",
          icon: Database,
        },
        {
          title: language === "ta" ? "புதிய ஜாதகம் கணிக்க" : "New Horoscope Calculation",
          href: "/horoscope",
          icon: Compass,
        },
        {
          title: language === "ta" ? "எனது சுயவிவரம்" : "My Profile & Account",
          href: "/dashboard",
          icon: User,
        },
        {
          title: language === "ta" ? "பிறந்தநாள் நினைவூட்டல்" : "Birthday Wishes & Alerts",
          action: () => setIsBirthdayOpen(true),
          icon: Cake,
        },
      ],
    },
    {
      id: "resources",
      label: language === "ta" ? "ஆதாரங்கள்" : "Resources",
      icon: BookOpen,
      href: "/vastu",
      isActive: false,
      hasDropdown: true,
      children: [
        {
          title: language === "ta" ? "வாஸ்து சாஸ்திரம் வழிகாட்டி" : "Vastu Classical Architecture",
          href: "/vastu",
          icon: Home,
        },
        {
          title: language === "ta" ? "பரிகாரங்கள் & வழிமுறைகள்" : "Remedies & Vedic Mantras",
          href: "/remedies",
          icon: Flame,
        },
        {
          title: language === "ta" ? "சுப முகூர்த்த காலண்டர்" : "Auspicious Dates Finder",
          href: "/muhurta",
          icon: Calendar,
        },
        {
          title: language === "ta" ? "எஃபிமெரிஸ் கணித உறுதிமொழி" : "XALEN Ephemeris Core",
          href: "/dashboard",
          icon: Activity,
        },
      ],
    },
    {
      id: "training",
      label: language === "ta" ? "பயிற்சி" : "Training",
      icon: GraduationCap,
      href: "#",
      isActive: false,
      hasDropdown: true,
      children: [
        {
          title: language === "ta" ? "தள வழிகாட்டி & ஆவணங்கள்" : "Platform Help & Guide",
          action: () => setIsHelpOpen(true),
          icon: BookOpen,
        },
        {
          title: language === "ta" ? "கே.பி. மற்றும் வேத முறைகள் விளக்கம்" : "KP & Vedic Calculation Guide",
          action: () => setIsHelpOpen(true),
          icon: GraduationCap,
        },
      ],
    },
    {
      id: "dashboard",
      label: language === "ta" ? "Dashboard" : "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard",
      isActive: pathname === "/dashboard" || pathname.startsWith("/admin"),
      hasDropdown: true,
      children: [
        {
          title: language === "ta" ? "பயனர் டாஷ்போர்டு" : "User Dashboard Overview",
          href: "/dashboard",
          icon: LayoutDashboard,
        },
        ...(role === "admin"
          ? [
              {
                title: language === "ta" ? "நிர்வாகி போர்டல் (Admin)" : "Administrator Portal",
                href: "/admin",
                icon: Shield,
              },
            ]
          : []),
      ],
    },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 w-full bg-white border-b border-[#D9DEE7] shadow-xs">
        {/* Top Header Bar (Level 1) */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="h-14 flex items-center justify-between gap-3 sm:gap-6">
            {/* 1. Brand Logo & Name */}
            <div className="flex items-center gap-3 sm:gap-6">
              <Link
                href={isAuthenticated ? "/" : "/login"}
                className="flex items-center gap-2.5 shrink-0 group focus:outline-hidden"
                aria-label="Gokul’s Astrological Insights Home"
              >
                <div className="w-8 h-8 rounded-lg bg-[#153F6B] flex items-center justify-center text-white shadow-xs border border-[#B4872B]/30 group-hover:scale-105 transition-transform">
                  <Sparkles className="w-4 h-4 text-[#B4872B] transition-transform group-hover:rotate-12" />
                </div>
                <div className="min-w-0">
                  <div className="font-serif text-base sm:text-lg font-bold text-[#153F6B] tracking-tight leading-tight truncate">
                    {t.brandName}
                  </div>
                  <div className="text-[10px] text-[#8190A6] truncate hidden lg:block">
                    {language === "ta"
                      ? "துல்லிய வேத & கே.பி வானியல் தளம்"
                      : "Precision Vedic & KP Astronomical System"}
                  </div>
                </div>
              </Link>

              {/* 2. Top Compact Search Bar */}
              {isAuthenticated && !isLoginPage && (
                <div className="hidden sm:flex items-center max-w-xs md:max-w-sm w-full">
                  <HeaderSearch />
                </div>
              )}
            </div>

            {/* 3. Controls: Help, Language, Log Out, User Avatar */}
            <div className="flex items-center gap-2 sm:gap-3 shrink-0">
              {/* Language Switcher */}
              <button
                type="button"
                onClick={toggleLanguage}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-xs font-semibold text-[#183047] transition-all cursor-pointer shadow-2xs"
                aria-label="Toggle language"
              >
                <Globe className="w-3.5 h-3.5 text-[#153F6B]" />
                <span className="text-xs">{language === "en" ? "தமிழ்" : "English"}</span>
              </button>

              {/* Support / Help Headphones Button */}
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={() => setIsHelpOpen(true)}
                  className="p-1.5 sm:px-2.5 sm:py-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-[#F2F3F5] text-xs font-semibold text-[#183047] transition-all cursor-pointer shadow-2xs inline-flex items-center gap-1"
                  aria-label="Support & Help"
                  title={language === "ta" ? "உதவி & வழிகாட்டி" : "Support & Help"}
                >
                  <Headphones className="w-4 h-4 text-[#153F6B]" />
                  <span className="hidden md:inline">{language === "ta" ? "உதவி" : "Help"}</span>
                </button>
              )}

              {/* Log Out Button */}
              {isAuthenticated && (
                <button
                  type="button"
                  onClick={logout}
                  className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg border border-[#D9DEE7] bg-white hover:bg-rose-50 text-xs font-semibold text-[#183047] hover:text-rose-600 transition-all cursor-pointer shadow-2xs"
                  aria-label="Log out"
                  title={t.navLogout || "Log Out"}
                >
                  <LogOut className="w-3.5 h-3.5 text-[#8190A6] group-hover:text-rose-600" />
                  <span className="hidden sm:inline">{language === "ta" ? "வெளியேறு" : "Log Out"}</span>
                </button>
              )}

              {/* User Avatar Circle */}
              {!isLoading && (
                <>
                  {isAuthenticated && user ? (
                    <div className="relative" ref={dropdownRef}>
                      <button
                        type="button"
                        onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                        className="w-8 h-8 rounded-full bg-[#153F6B] text-white border-2 border-[#B4872B] flex items-center justify-center font-bold text-xs shadow-xs hover:scale-105 transition-transform cursor-pointer"
                        aria-expanded={userDropdownOpen}
                        aria-label="User Profile"
                        title={user.displayName || user.username}
                      >
                        {user.username?.charAt(0).toUpperCase() || "G"}
                      </button>

                      {userDropdownOpen && (
                        <div
                          className="absolute right-0 mt-2 w-56 rounded-2xl shadow-xl bg-white border border-[#D9DEE7] py-2 z-50 divide-y divide-[#F2F3F5] animate-in fade-in duration-150"
                        >
                          <div className="px-4 py-2.5 text-xs">
                            <div className="font-bold text-[#183047] truncate">
                              {user.displayName || user.username}
                            </div>
                            <div className="truncate text-[11px] text-[#8190A6]">
                              {user.email || `@${user.username}`}
                            </div>
                            <div className="mt-1 flex items-center gap-1.5">
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-semibold bg-[#EBF2FE] text-[#153F6B] border border-[#BFDBFE]">
                                <Shield className="w-2.5 h-2.5 text-[#153F6B]" />
                                {user.role === "admin" ? "Administrator" : "Standard User"}
                              </span>
                            </div>
                          </div>

                          <div className="py-1">
                            <Link
                              href="/dashboard"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#183047] hover:bg-[#F2F3F5] transition-colors"
                            >
                              <LayoutDashboard className="w-3.5 h-3.5 text-[#153F6B]" />
                              <span>{t.navDashboard || "Dashboard"}</span>
                            </Link>

                            <Link
                              href="/horoscopes"
                              onClick={() => setUserDropdownOpen(false)}
                              className="flex items-center gap-2.5 px-4 py-2 text-xs text-[#183047] hover:bg-[#F2F3F5] transition-colors"
                            >
                              <Database className="w-3.5 h-3.5 text-[#B4872B]" />
                              <span>{language === "ta" ? "சேமிக்கப்பட்ட ஜாதகங்கள்" : "Saved Horoscopes"}</span>
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
                              <span>{t.navLogout || "Log Out"}</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    !isLoginPage && (
                      <Link
                        href="/login"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#153F6B] bg-[#153F6B] hover:bg-[#0F3155] text-xs font-semibold text-white shadow-xs transition-colors"
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
                  className="md:hidden p-1.5 rounded-lg text-[#183047] hover:bg-[#F2F3F5] border border-[#D9DEE7]"
                  aria-label="Open mobile navigation menu"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Main Navigation Row (Level 2) - VedicSage Reference Navigation */}
        {isAuthenticated && !isLoginPage && (
          <div className="hidden md:block border-t border-[#D9DEE7] bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <nav
                className="h-10.5 flex items-center gap-1 sm:gap-2 overflow-visible"
                aria-label="Secondary Navigation Bar"
              >
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isMenuOpen = activeDropdown === item.id;

                  if (!item.hasDropdown) {
                    return (
                      <Link
                        key={item.id}
                        href={item.href}
                        className={`inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium transition-all relative ${
                          item.isActive
                            ? "text-[#153F6B] font-bold border-b-2 border-[#B4872B]"
                            : "text-[#183047] hover:text-[#153F6B] hover:bg-[#F2F3F5] rounded-t-md"
                        }`}
                      >
                        <Icon
                          className={`w-3.5 h-3.5 ${
                            item.isActive ? "text-[#153F6B]" : "text-[#8190A6]"
                          }`}
                        />
                        <span>{item.label}</span>
                      </Link>
                    );
                  }

                  return (
                    <div
                      key={item.id}
                      className="relative"
                      onMouseEnter={() => setActiveDropdown(item.id)}
                      onMouseLeave={() => setActiveDropdown(null)}
                    >
                      <button
                        type="button"
                        onClick={() => setActiveDropdown(isMenuOpen ? null : item.id)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium transition-all cursor-pointer relative ${
                          item.isActive
                            ? "text-[#153F6B] font-bold border-b-2 border-[#B4872B]"
                            : "text-[#183047] hover:text-[#153F6B] hover:bg-[#F2F3F5] rounded-t-md"
                        }`}
                      >
                        <Icon
                          className={`w-3.5 h-3.5 ${
                            item.isActive ? "text-[#153F6B]" : "text-[#8190A6]"
                          }`}
                        />
                        <span>{item.label}</span>
                        <ChevronDown className="w-3 h-3 text-[#8190A6]" />
                      </button>

                      {/* Dropdown Menu Box */}
                      {isMenuOpen && item.children && (
                        <div
                          className="absolute left-0 top-full mt-0 w-64 rounded-xl shadow-xl bg-white border border-[#D9DEE7] py-1.5 z-50 animate-in fade-in duration-100"
                        >
                          {item.children.map((subItem, idx) => {
                            const SubIcon = subItem.icon;
                            if (subItem.action) {
                              return (
                                <button
                                  key={idx}
                                  type="button"
                                  onClick={() => {
                                    setActiveDropdown(null);
                                    subItem.action();
                                  }}
                                  className="w-full flex items-center gap-2.5 px-3.5 py-2 text-xs text-[#183047] hover:bg-[#F2F3F5] hover:text-[#153F6B] text-left transition-colors cursor-pointer"
                                >
                                  <SubIcon className="w-3.5 h-3.5 text-[#B4872B] shrink-0" />
                                  <span className="truncate">{subItem.title}</span>
                                </button>
                              );
                            }

                            return (
                              <Link
                                key={idx}
                                href={subItem.href}
                                onClick={() => setActiveDropdown(null)}
                                className="flex items-center gap-2.5 px-3.5 py-2 text-xs text-[#183047] hover:bg-[#F2F3F5] hover:text-[#153F6B] transition-colors"
                              >
                                <SubIcon className="w-3.5 h-3.5 text-[#153F6B] shrink-0" />
                                <span className="truncate">{subItem.title}</span>
                              </Link>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </nav>
            </div>
          </div>
        )}

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[#D9DEE7] bg-white px-4 pt-3 pb-5 space-y-4 shadow-lg animate-in slide-in-from-top-2 duration-150 max-h-[85vh] overflow-y-auto">
            {/* Mobile Search */}
            <div className="pt-1">
              <HeaderSearch />
            </div>

            {/* Mobile Navigation Links */}
            <nav className="flex flex-col space-y-2" aria-label="Mobile Navigation">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <div key={item.id} className="space-y-1">
                    <Link
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-bold ${
                        item.isActive
                          ? "bg-[#EBF2FE] text-[#153F6B]"
                          : "text-[#183047] hover:bg-[#F2F3F5]"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className="w-4 h-4 text-[#153F6B]" />
                        <span>{item.label}</span>
                      </div>
                    </Link>

                    {item.children && (
                      <div className="pl-6 space-y-1">
                        {item.children.map((sub, sIdx) => {
                          const SubIcon = sub.icon;
                          if (sub.action) {
                            return (
                              <button
                                key={sIdx}
                                type="button"
                                onClick={() => {
                                  setMobileMenuOpen(false);
                                  sub.action();
                                }}
                                className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-[#52667E] hover:text-[#153F6B] text-left"
                              >
                                <SubIcon className="w-3 h-3 text-[#B4872B]" />
                                <span className="truncate">{sub.title}</span>
                              </button>
                            );
                          }
                          return (
                            <Link
                              key={sIdx}
                              href={sub.href}
                              onClick={() => setMobileMenuOpen(false)}
                              className="flex items-center gap-2 px-2.5 py-1.5 text-xs text-[#52667E] hover:text-[#153F6B]"
                            >
                              <SubIcon className="w-3 h-3 text-[#153F6B]" />
                              <span className="truncate">{sub.title}</span>
                            </Link>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </nav>

            {/* Mobile Profile & Logout */}
            <div className="pt-3 border-t border-[#D9DEE7] flex items-center justify-between">
              {isAuthenticated && user && (
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-[#153F6B] text-white flex items-center justify-center text-xs font-bold border border-[#B4872B]">
                    {user.username?.charAt(0).toUpperCase() || "G"}
                  </div>
                  <div>
                    <div className="text-xs font-bold text-[#183047]">
                      {user.displayName || user.username}
                    </div>
                    <div className="text-[10px] text-[#8190A6]">@{user.username}</div>
                  </div>
                </div>
              )}

              <button
                type="button"
                onClick={() => {
                  setMobileMenuOpen(false);
                  logout();
                }}
                className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-bold text-rose-600 hover:bg-rose-50 cursor-pointer"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>{language === "ta" ? "வெளியேறு" : "Log Out"}</span>
              </button>
            </div>
          </div>
        )}
      </header>

      {/* Guide & Help Modal */}
      <HelpModal isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />

      {/* Birthday Reminder Modal */}
      <BirthdayReminderModal
        isOpen={isBirthdayOpen}
        onClose={() => setIsBirthdayOpen(false)}
        autoCheckOnLogin={true}
      />
    </>
  );
}
