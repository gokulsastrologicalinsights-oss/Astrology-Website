"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { UpgradeModal } from "@/components/common/UpgradeModal";
import { PermissionKey } from "@/lib/permissions";
import {
  Compass,
  Clock,
  Grid,
  Sparkles,
  Layers,
  Calendar,
  Database,
  Cake,
  BookOpen,
  HeartHandshake,
  Heart,
  ShieldCheck,
  Hash,
  Briefcase,
  Zap,
  ShieldAlert,
  Flame,
  Star,
  Crown,
  Lock,
  ArrowRight,
} from "lucide-react";
import { BirthdayReminderModal } from "@/components/birthday/BirthdayReminderModal";
import { DasaCautionReminderModal } from "@/components/caution/DasaCautionReminderModal";

export default function AstrologyToolsPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const { user, isAuthenticated, isLoading, hasPermission } = useAuth();
  const [isBirthdayOpen, setIsBirthdayOpen] = useState(false);
  const [isCautionOpen, setIsCautionOpen] = useState(false);

  // Upgrade Modal State for locked tools
  const [upgradeModalState, setUpgradeModalState] = useState<{
    isOpen: boolean;
    toolNameEn: string;
    toolNameTa: string;
    requiredPlan: "basic" | "tamil_specialist" | "pro";
  }>({
    isOpen: false,
    toolNameEn: "",
    toolNameTa: "",
    requiredPlan: "pro",
  });

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace("/login");
    }
  }, [isAuthenticated, user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-14rem)] flex items-center justify-center bg-[#F2F3F5]">
        <div className="w-8 h-8 border-4 border-[#153F6B] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  interface AstrologyToolCard {
    id: string;
    titleTa: string;
    titleEn: string;
    descriptionTa?: string;
    descriptionEn?: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    requiredPermission?: PermissionKey;
    requiredPlan?: "basic" | "tamil_specialist" | "pro";
  }

  // Section 1: Astrology Tools Cards
  const astrologyTools: AstrologyToolCard[] = [
    {
      id: "master-prediction",
      titleTa: "மகா முழுமை கணிப்பு (Master Prediction Suite)",
      titleEn: "Master Prediction Suite (All-In-One)",
      descriptionTa: "ஜாதகத்தை திறந்ததும் KP நிகழ்வு கணிப்பு, 1-5 ஆண்டு காலவரிசை, திருமண கணிப்பு, அஷ்டகவர்க்கம், இரட்டை கோச்சாரம், கக்ஷா & 28 நட்சத்திர ஆய்வு அத்தனையும் ஒரே திரையில்.",
      descriptionEn: "Complete unified predictive suite: KP Monthly Timing, Multi-Year Roadmap, Marriage Engine, Double Transit, Ashtakavarga & Kaksha, 28 Nakshatras, and Horary in a single screen.",
      href: "/tools/master-prediction",
      icon: Crown,
      color: "text-amber-900 border-amber-400 bg-gradient-to-r from-amber-100/90 to-yellow-50/90 ring-2 ring-amber-500/50 shadow-md",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "kp-daily-horoscope",
      titleTa: "கே.பி. தினசரி, வார & மாத ராசிபலன் (கோச்சார கணிப்பு)",
      titleEn: "KP Daily, Weekly & Monthly Horoscope & Transits",
      descriptionTa: "12 ராசிகளுக்கும் தினசரி, வார மற்றும் மாதாந்திர ராசிபலன், நிகழ்நேர கிரகப் பெயர்ச்சிகள், கோச்சார பலன் சுருக்கம், சந்திராஷ்டமம் மற்றும் 5 அம்ச வழிகாட்டல்.",
      descriptionEn: "Comprehensive Daily, Weekly & Monthly predictions for all 12 Rashis with planetary transit movements, house Gochara synthesis, and Chandrashtama alerts.",
      href: "/tools/kp-daily-horoscope",
      icon: Clock,
      color: "text-purple-700 border-purple-400 bg-purple-50/90 ring-2 ring-purple-500/40",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "kalachakra",
      titleTa: "காலச்சக்கரம்: தற்போதைய தசா-புத்தி மற்றும் கோச்சார ரேடார்",
      titleEn: "KalaChakra: Current Period & Cosmic Weather",
      descriptionTa: "நிகழ்கால விம்சோத்தரி தசா-புக்தி, தற்போதைய கோச்சார கிரக நிலைகள் (சனி, குரு, ராகு-கேது) மற்றும் கே.பி நிகழ்வு சாத்தியக்கூறுகள் வழிகாட்டி.",
      descriptionEn: "Precision real-time life timing engine combining Vimshottari Dasa-Bhukti, live planetary transits, and KP event probability signals.",
      href: "/tools/kalachakra",
      icon: Compass,
      color: "text-indigo-700 border-indigo-400 bg-indigo-50/90 ring-2 ring-indigo-500/40",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "instant-revelation",
      titleTa: "வாடிக்கையாளர் நேரடி வாக்கு பலகை (உடனடி பலன்)",
      titleEn: "Instant Customer Revelation Teleprompter",
      descriptionTa: "வாடிக்கையாளர் வந்தவுடன் எவ்வித கிரகக் கணக்கீடும் இன்றி வருகை நோக்கம், 3 கடந்த கால உண்மைகள், மற்றும் எதிர்காலத்தை நேரடியாகப் பேசும் வாக்கு பலகை.",
      descriptionEn: "Zero-analysis cold-reading teleprompter: instant arrival mind-reading, 3 verifiable past shock hits, Vastu markers, and future timing windows.",
      href: "/tools/instant-revelation",
      icon: Zap,
      color: "text-rose-700 border-rose-300 bg-rose-50/70 ring-2 ring-rose-400/40",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "horoscope",
      titleTa: "ஜாதகம் (வேத & கே.பி)",
      titleEn: "Horoscope (Vedic & KP)",
      href: "/tools/horoscope",
      icon: Compass,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
      requiredPermission: "vedic",
      requiredPlan: "basic",
    },
    {
      id: "horoscope-writing",
      titleTa: "பாரம்பரிய தமிழ் ஜாதகக் குறிப்பு (6-பக்க ஏடு)",
      titleEn: "Traditional Tamil Horoscope Writing",
      descriptionTa: "பாரம்பரிய 6-பக்க தமிழ் ஜாதக ஏடு, தினசுத்தி, நாழிகை வினாழிகை, உடுமகா திசை மற்றும் அர்ச்சனை சீட்டு.",
      descriptionEn: "Traditional 6-page Tamil horoscope booklet, eras, Vimshottari Dasa, Nazhigai conversion, and archana slip.",
      href: "/tools/horoscope-writing",
      icon: BookOpen,
      color: "text-[#8B6914] border-[#B4872B]/40 bg-[#FAF2DE]/50",
      requiredPermission: "tamil_horoscope",
      requiredPlan: "tamil_specialist",
    },
    {
      id: "kp-narrative",
      titleTa: "கே.பி. கணிப்பு உரை அறிக்கை (Predictive Narrative)",
      titleEn: "Automated KP Predictive Narrative Engine",
      descriptionTa: "ஜாதக வாக்குறுதி, தற்போதைய தசா-புத்தி பலன்கள், 12-24 மாத மைல்கற்கள் மற்றும் பரிகாரங்களை எளிய நடையில் வழங்கும் கணிப்பு இயந்திரம்.",
      descriptionEn: "Structured, plain-language predictive report evaluating Natal Event Promise, running Dasha-Bhukti, 12-24 month milestone windows, and remedial advice.",
      href: "/tools/kp-predictive-narrative",
      icon: Sparkles,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE] ring-2 ring-[#153F6B]/20",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "love-or-arranged-marriage",
      titleTa: "காதல் அல்லது நிச்சயிக்கப்பட்ட திருமணம் (Love vs Arranged)",
      titleEn: "Love vs. Arranged Marriage Predictor",
      descriptionTa: "ஜாதகத்தில் காதல் திருமணமா அல்லது பெற்றோர்களால் நிச்சயிக்கப்படும் திருமணமா என்பதை துல்லியமாக அறியும் எளிய கணிப்பான்.",
      descriptionEn: "Instant, straightforward verdict on whether the entered horoscope indicates Love Marriage, Arranged Marriage, or Love-cum-Arranged with parental blessings.",
      href: "/tools/love-or-arranged-marriage",
      icon: Heart,
      color: "text-rose-700 border-rose-300 bg-rose-50/80 ring-2 ring-rose-400/40 shadow-sm",
      requiredPermission: "marriage_matching",
      requiredPlan: "basic",
    },
    {
      id: "marriage",
      titleTa: "திருமணப் பொருத்தம் (36 அஷ்டகூடம்)",
      titleEn: "Kundli Matching & 36 Ashta Kuta",
      href: "/tools/marriage-compatibility",
      icon: HeartHandshake,
      color: "text-[#153F6B] border-[#153F6B]/30 bg-[#EBF2FE]",
      requiredPermission: "marriage_matching",
      requiredPlan: "basic",
    },
    {
      id: "panchang",
      titleTa: "தினசரி பஞ்சாங்கம் & 24-கிரக ஹோரை",
      titleEn: "Daily Panchangam & 24-Planetary Horas",
      descriptionTa: "சூரிய உதயம், திதி, நட்சத்திரம், யோகம், கரணம், இராகு காலம் மற்றும் நேரடி 24-மணி நேர கிரக ஹோரை வழிகாட்டி.",
      descriptionEn: "Astronomical 5-limbs, Rahu/Yama/Gulika octants, and live 24-Hora timing advisor with real-time countdown.",
      href: "/tools/panchang",
      icon: Calendar,
      color: "text-amber-600 border-amber-300 bg-amber-50",
      requiredPermission: "panchang_muhurta",
      requiredPlan: "basic",
    },
    {
      id: "birth-time-rectification",
      titleTa: "பிறந்த நேர திருத்தம் (BTR)",
      titleEn: "Birth Time Rectification (BTR)",
      descriptionTa: "வாழ்க்கை நிகழ்வுகளைக் கொண்டு கே.பி உப-அதிபதி, D9 நவாம்சம் & D60 ஷஷ்டியாம்சம் முறையில் வினாடித் துல்லியத்தில் நேரத் திருத்தம்.",
      descriptionEn: "Rectify birth time down to the second using past life events, KP sub-lords, D9 Navamsha, and D60 Shashtiamsha shifts.",
      href: "/tools/birth-time-rectification",
      icon: Clock,
      color: "text-amber-700 border-amber-300 bg-amber-50",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "brighu-naadi",
      titleTa: "பிருகு நந்தி நாடி விதிகள் (Bhrigu Nandi Nadi)",
      titleEn: "Bhrigu Nandi Nadi (BNN) Analysis",
      descriptionTa: "ஜீவ காரகன் குரு, கர்ம காரகன் சனி, சுக்கிரன் மற்றும் செவ்வாய் கிரக சேர்க்கைகள் மூலம் தொழில், குடும்பம், விதி பலன்கள்.",
      descriptionEn: "Classical Bhrigu Nandi Nadi planetary combinations evaluating Jiva Karaka (Guru), Karma Karaka (Shani), and directional triads.",
      href: "/tools/brighu-naadi",
      icon: BookOpen,
      color: "text-amber-800 border-amber-300 bg-amber-50",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "advanced-kp",
      titleTa: "உயர்நிலை கே.பி (249 உப-அதிபதிகள்)",
      titleEn: "Advanced KP System (249 Sub-Lords)",
      href: "/tools/advanced-kp",
      icon: Layers,
      color: "text-indigo-600 border-indigo-300 bg-indigo-50",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "kp-events",
      titleTa: "கே.பி. நிகழ்வு கணிப்பு (110 நிகழ்வுகள்)",
      titleEn: "KP Events & Prediction (110 Events)",
      href: "/tools/kp-events-prediction",
      icon: Sparkles,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "numerology",
      titleTa: "எண் கணித அரங்கம் & லோ ஷு கிரிட்",
      titleEn: "Numerology Studio & Lo Shu",
      href: "/tools/numerology",
      icon: Hash,
      color: "text-blue-600 border-blue-300 bg-blue-50",
      requiredPermission: "numerology",
      requiredPlan: "pro",
    },
    {
      id: "muhurta",
      titleTa: "சுப முகூர்த்த அரங்கம்",
      titleEn: "Muhurta Event Matching Studio",
      descriptionTa: "திருமணம், கிரகப்பிரவேசம், வர்த்தகத் துவக்கம் மற்றும் வாகன முகூர்த்தங்களுக்கான சாஸ்திர தேர்வு இயந்திரம்.",
      descriptionEn: "Multi-criteria candidate search and scoring engine for Marriage, Griha Pravesha, Business Launch, and Vehicle Purchase.",
      href: "/tools/muhurta",
      icon: Sparkles,
      color: "text-emerald-600 border-emerald-300 bg-emerald-50",
      requiredPermission: "panchang_muhurta",
      requiredPlan: "basic",
    },
    {
      id: "jamakkol-prasanam",
      titleTa: "ஜாமக்கோள் பிரசன்னம் (16-ஜாம சக்கரம்)",
      titleEn: "Jamakkol Prasanam Horary",
      descriptionTa: "உதயம், ஆருடம், கவிப்பு மற்றும் 8 வெளிவட்ட ஜாமக் கோள்களைக் கொண்ட அதிவேக 16-ஜாம பிரசன்ன சக்கரம் & காரிய சித்தி தீர்ப்பு.",
      descriptionEn: "Classical 16-Jamam horary astrology engine with Udhayam, Aarudham, Kavippu, and 8 outer Jama Grahas in a dual-ring South Indian chart.",
      href: "/tools/jamakkol-prasanam",
      icon: Compass,
      color: "text-amber-600 border-amber-300 bg-amber-50",
      requiredPermission: "kp_astrology",
      requiredPlan: "pro",
    },
    {
      id: "pancha-pakshi",
      titleTa: "பஞ்ச பட்சி சாஸ்திரம் (அகத்தியர் முறை)",
      titleEn: "Pancha Pakshi Shastra",
      descriptionTa: "அகத்தியர் சித்த முறைப்படி வல்லூறு, ஆந்தை, காகம், கோழி, மயில் ஐந்து பட்சிகளின் அரசு, ஊண், நடை, துயில், சாவு அந்தர கால வழிகாட்டி.",
      descriptionEn: "Sage Agastya's five-bird bio-rhythm predictive system across Ruling, Eating, Walking, Sleeping, and Dying phases.",
      href: "/tools/pancha-pakshi",
      icon: Zap,
      color: "text-teal-600 border-teal-300 bg-teal-50",
      requiredPermission: "panchang_muhurta",
      requiredPlan: "pro",
    },
    {
      id: "daily-sastra",
      titleTa: "தினசரி சாஸ்திர வழிகாட்டி",
      titleEn: "Daily Dharma & Sastra Guide",
      descriptionTa: "நாள்விழிப்பு, கௌரி பஞ்சாங்கம், வாரசூலம் பரிகாரம், 22 நோய் தீர்க்கும் தெய்வங்கள், வாஸ்து புருஷன் விழிப்பு மற்றும் சுபமுகூர்த்த நியதிகள்.",
      descriptionEn: "Classical daily do's and don'ts, Gowri Panchangam, Soolam remedies, medical deity healing, and Vastu Purusha awakening.",
      href: "/tools/daily-sastra",
      icon: ShieldCheck,
      color: "text-indigo-700 border-indigo-300 bg-indigo-50",
      requiredPermission: "remedies",
      requiredPlan: "basic",
    },
    {
      id: "kuladeivam-finder",
      titleTa: "குலதெய்வம் கண்டறியும் ஆய்வு அரங்கம்",
      titleEn: "Kuladeivam (Family Deity) Finder",
      descriptionTa: "5 & 9-ஆம் பாவகங்கள், நவாம்சம் மற்றும் ஜாமக்கோள் பிரசன்ன ஆருட வழி வம்சக் குலதெய்வம், கோவில் திசை, மற்றும் பரிகார வழிகாட்டி.",
      descriptionEn: "Classical Vedic & Horary engine to find ancestral deity, gender, worship category, temple direction, and discovery protocol.",
      href: "/tools/kuladeivam-finder",
      icon: Sparkles,
      color: "text-amber-800 border-amber-400 bg-amber-50",
      requiredPermission: "remedies",
      requiredPlan: "basic",
    },
    {
      id: "remedies",
      titleTa: "சாஸ்திர பரிகாரங்கள் & நவகிரக திருத்தலங்கள்",
      titleEn: "Shastric Remedies & Navagraha Temples",
      descriptionTa: "சாஸ்திர தோஷ நிவர்த்தி பரிகாரங்கள், 9 நவகிரக பரிகாரத் தலங்கள், மந்திர ஜபங்கள், மற்றும் ஹோம சாந்தி வழிகாட்டி.",
      descriptionEn: "Classical Vedic dosha remedies, 9 Navagraha planetary temples, Japa mantras, Daanam, and Shastric Pariharam guide.",
      href: "/remedies",
      icon: Sparkles,
      color: "text-amber-700 border-amber-300 bg-amber-50",
      requiredPermission: "remedies",
      requiredPlan: "basic",
    },
  ];

  // Section 2: Workspace / Practice Cards
  const workspaceTools = [
    {
      id: "saved-charts",
      titleTa: "சேமிக்கப்பட்ட ஜாதகங்கள்",
      titleEn: "Saved Horoscopes",
      href: "/horoscopes",
      icon: Database,
      color: "text-[#B4872B] border-[#B4872B]/40 bg-[#FAF2DE]/50",
      requiredPermission: "vedic" as PermissionKey,
      requiredPlan: "basic" as const,
    },
    {
      id: "birthdays",
      titleTa: "பிறந்தநாள் நினைவூட்டல்",
      titleEn: "Birthday Reminders",
      action: () => setIsBirthdayOpen(true),
      icon: Cake,
      color: "text-amber-600 border-amber-300 bg-amber-50",
      requiredPermission: "crm" as PermissionKey,
      requiredPlan: "tamil_specialist" as const,
    },
    {
      id: "caution-alerts",
      titleTa: "கண்ட கால எச்சரிக்கை (Dasa Caution)",
      titleEn: "Dasa Caution Alerts",
      action: () => setIsCautionOpen(true),
      icon: ShieldAlert,
      color: "text-rose-600 border-rose-300 bg-rose-50",
      requiredPermission: "crm" as PermissionKey,
      requiredPlan: "tamil_specialist" as const,
    },
    {
      id: "instant-revelation",
      titleTa: "நேரடி வாக்கு பலகை",
      titleEn: "Instant Revelation",
      href: "/tools/instant-revelation",
      icon: Flame,
      color: "text-rose-700 border-rose-300 bg-rose-50/70",
      requiredPermission: "kp_astrology" as PermissionKey,
      requiredPlan: "pro" as const,
    },
  ];

  const handleCardClick = (
    e: React.MouseEvent,
    card: {
      titleEn: string;
      titleTa: string;
      requiredPermission?: PermissionKey;
      requiredPlan?: "basic" | "tamil_specialist" | "pro";
    }
  ) => {
    if (card.requiredPermission && !hasPermission(card.requiredPermission)) {
      e.preventDefault();
      setUpgradeModalState({
        isOpen: true,
        toolNameEn: card.titleEn,
        toolNameTa: card.titleTa,
        requiredPlan: card.requiredPlan || "pro",
      });
    }
  };

  const isProUser = user?.role === "admin" || user?.subscription?.tier === "pro";
  const isTamilUser = isProUser || user?.subscription?.tier === "tamil_specialist";

  return (
    <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-6 sm:py-8 space-y-8">
      {/* Breadcrumb Navigation */}
      <Breadcrumbs
        items={[
          {
            label: language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools",
          },
        ]}
      />

      {/* Subscription Status & Upgrade CTA Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-[#153F6B] via-[#1E4E82] to-[#B4872B] p-4 sm:p-5 text-white flex flex-col sm:flex-row items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3.5 text-center sm:text-left">
          <div className="w-11 h-11 rounded-full bg-white/10 border border-white/20 flex items-center justify-center shrink-0">
            <Crown className="w-6 h-6 text-amber-300" />
          </div>
          <div>
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h3 className="text-sm sm:text-base font-bold">
                {language === "ta"
                  ? "தொழில்முறை ஜோதிட மென்பொருள் தொகுப்பு (Paid Service)"
                  : "Professional Astrology Software Workstation"}
              </h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-400 text-stone-900">
                {isProUser
                  ? "PRO ACTIVE"
                  : isTamilUser
                  ? "TAMIL PRO ACTIVE"
                  : "FREE TIER"}
              </span>
            </div>
            <p className="text-xs text-slate-200 mt-0.5">
              {language === "ta"
                ? "தமிழ் ஜாதக ஏடு, கே.பி. 249 பிரசன்னம், ஜாமக்கோள் & எண் கணிதத்தை வரம்பற்ற அணுகலில் பெற சந்தா திட்டத்தை ஆக்டிவேட் செய்யவும்."
                : "Swiss Ephemeris precision, 6-page Tamil booklets, KP 249 horary, Jamakkol, and unlimited PDF exports."}
            </p>
          </div>
        </div>

        <Link
          href="/pricing"
          className="py-2.5 px-5 rounded-xl bg-amber-400 hover:bg-amber-300 text-stone-900 font-extrabold text-xs sm:text-sm tracking-wide shadow-sm hover:shadow transition-all shrink-0 flex items-center gap-1.5"
        >
          <span>
            {isProUser
              ? language === "ta"
                ? "திட்டங்களை நிர்வகிக்க"
                : "Manage Subscription"
              : language === "ta"
              ? "கட்டண திட்டங்களைக் காண்க"
              : "View Plans & Pricing"}
          </span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Section 1: ஜோதிடக் கருவிகள் (Astrology Tools) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <Layers className="w-5 h-5 text-[#B4872B]" />
            <h2 className="text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta" ? "ஜோதிடக் கருவிகள்" : "Astrology Tools"}
            </h2>
          </div>
          <div className="flex-1 h-px bg-[#D9DEE7]" />
          <Link
            href="/pricing"
            className="text-xs font-bold text-[#153F6B] hover:text-[#B4872B] transition-colors shrink-0 flex items-center gap-1"
          >
            <span>{language === "ta" ? "திட்டங்கள் & விலை" : "Plans & Pricing"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 sm:gap-4">
          {astrologyTools.map((card) => {
            const Icon = card.icon;
            const isLocked = card.requiredPermission
              ? !hasPermission(card.requiredPermission)
              : false;

            return (
              <Link
                key={card.id}
                href={card.href}
                onClick={(e) => handleCardClick(e, card)}
                title={
                  (language === "ta" ? card.descriptionTa : card.descriptionEn) ||
                  (language === "ta" ? card.titleTa : card.titleEn)
                }
                className={`relative h-28 sm:h-32 rounded-xl bg-white border p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs transition-all group ${
                  isLocked
                    ? "border-amber-200/80 hover:border-amber-400 bg-amber-50/20"
                    : "border-[#D9DEE7] hover:border-[#B4872B] hover:shadow-md"
                }`}
              >
                {/* Plan Badge */}
                {card.requiredPlan === "pro" && (
                  <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider bg-indigo-100 text-indigo-800 border border-indigo-200">
                    PRO
                  </span>
                )}
                {card.requiredPlan === "tamil_specialist" && (
                  <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-300">
                    TAMIL PRO
                  </span>
                )}

                {/* Locked Indicator */}
                {isLocked && (
                  <div className="absolute top-2 left-2 p-1 rounded-full bg-amber-100 text-amber-700 shadow-2xs">
                    <Lock className="w-3 h-3" />
                  </div>
                )}

                <div
                  className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                >
                  <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                  {language === "ta" ? card.titleTa : card.titleEn}
                </div>
                <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                  {language === "ta" ? card.titleEn : card.titleTa}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Section 2: என் பயிற்சி (My Workspace / Practice) */}
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 shrink-0">
            <Briefcase className="w-5 h-5 text-[#B4872B]" />
            <h2 className="text-base sm:text-lg font-bold text-[#183047]">
              {language === "ta" ? "என் பயிற்சி" : "My Practice"}
            </h2>
          </div>
          <div className="flex-1 h-px bg-[#D9DEE7]" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-4 gap-3 sm:gap-4">
          {workspaceTools.map((card) => {
            const Icon = card.icon;
            const isLocked = card.requiredPermission
              ? !hasPermission(card.requiredPermission)
              : false;

            if (card.action) {
              return (
                <button
                  key={card.id}
                  type="button"
                  onClick={(e) => {
                    if (isLocked) {
                      setUpgradeModalState({
                        isOpen: true,
                        toolNameEn: card.titleEn,
                        toolNameTa: card.titleTa,
                        requiredPlan: card.requiredPlan || "pro",
                      });
                    } else {
                      card.action();
                    }
                  }}
                  className={`relative h-28 sm:h-32 rounded-xl bg-white border p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs transition-all group cursor-pointer ${
                    isLocked
                      ? "border-amber-200/80 hover:border-amber-400 bg-amber-50/20"
                      : "border-[#D9DEE7] hover:border-[#B4872B] hover:shadow-md"
                  }`}
                >
                  {isLocked && (
                    <div className="absolute top-2 left-2 p-1 rounded-full bg-amber-100 text-amber-700 shadow-2xs">
                      <Lock className="w-3 h-3" />
                    </div>
                  )}
                  {card.requiredPlan === "tamil_specialist" && (
                    <span className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[8px] font-black uppercase tracking-wider bg-amber-100 text-amber-800 border border-amber-300">
                      CRM
                    </span>
                  )}
                  <div
                    className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                  >
                    <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                    {language === "ta" ? card.titleTa : card.titleEn}
                  </div>
                  <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                    {language === "ta" ? card.titleEn : card.titleTa}
                  </div>
                </button>
              );
            }

            return (
              <Link
                key={card.id}
                href={card.href!}
                onClick={(e) => handleCardClick(e, card)}
                className={`relative h-28 sm:h-32 rounded-xl bg-white border p-2.5 sm:p-3 flex flex-col items-center justify-center text-center shadow-xs transition-all group ${
                  isLocked
                    ? "border-amber-200/80 hover:border-amber-400 bg-amber-50/20"
                    : "border-[#D9DEE7] hover:border-[#B4872B] hover:shadow-md"
                }`}
              >
                {isLocked && (
                  <div className="absolute top-2 left-2 p-1 rounded-full bg-amber-100 text-amber-700 shadow-2xs">
                    <Lock className="w-3 h-3" />
                  </div>
                )}
                <div
                  className={`w-10 h-10 sm:w-11 sm:h-11 rounded-full border flex items-center justify-center mb-2 group-hover:scale-105 transition-transform ${card.color}`}
                >
                  <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
                </div>
                <div className="text-xs sm:text-sm font-semibold text-[#183047] group-hover:text-[#153F6B] leading-tight line-clamp-2">
                  {language === "ta" ? card.titleTa : card.titleEn}
                </div>
                <div className="text-[10px] text-[#8190A6] mt-0.5 truncate hidden sm:block">
                  {language === "ta" ? card.titleEn : card.titleTa}
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Engine & Calculation Integrity Banner */}
      <div className="p-4 rounded-2xl bg-white border border-[#D9DEE7] flex items-center gap-3 text-xs text-[#52667E] shadow-2xs">
        <ShieldCheck className="w-5 h-5 text-emerald-600 shrink-0" />
        <p className="leading-relaxed">
          <strong>{language === "ta" ? "துல்லியமான எஃபிமெரிஸ் கணிதம்:" : "Deterministic Ephemeris:"}</strong>{" "}
          {language === "ta"
            ? "அனைத்து கிரக நிலைகள், கே.பி. உப-அதிபதிகள் மற்றும் தசா காலங்கள் சுவிஸ் எஃபிமெரிஸ் மற்றும் XALEN வானியல் முறையின் மூலம் நேரடியாகக் கணக்கிடப்படுகின்றன."
            : "All planetary positions, KP cusps, and Dasa periods operate on verified astronomical formulas powered by the XALEN computational core."}
        </p>
      </div>

      {/* Modals */}
      <UpgradeModal
        isOpen={upgradeModalState.isOpen}
        onClose={() =>
          setUpgradeModalState((prev) => ({ ...prev, isOpen: false }))
        }
        toolNameEn={upgradeModalState.toolNameEn}
        toolNameTa={upgradeModalState.toolNameTa}
        requiredPlan={upgradeModalState.requiredPlan}
      />
      <BirthdayReminderModal isOpen={isBirthdayOpen} onClose={() => setIsBirthdayOpen(false)} />
      <DasaCautionReminderModal isOpen={isCautionOpen} onClose={() => setIsCautionOpen(false)} />
    </div>
  );
}
