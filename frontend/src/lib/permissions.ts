/**
 * Gokul's Astrological Insights - Subscription & Selected Access Permission Models
 * Defines module permissions, subscription tiers, and presets for renting/leasing the platform.
 */

export type PermissionKey =
  | "vedic"
  | "tamil_horoscope"
  | "kp_astrology"
  | "marriage_matching"
  | "panchang_muhurta"
  | "numerology"
  | "vastu"
  | "remedies"
  | "crm"
  | "pdf_export";

export type SubscriptionTier = "trial" | "basic" | "pro" | "enterprise" | "custom";
export type SubscriptionStatus = "active" | "suspended" | "expired" | "pending";

export interface UserPermissions {
  vedic: boolean;             // Parashari Vedic Charts, Shadbala, Ashtakavarga, Vargas D1-D60
  tamil_horoscope: boolean;   // Traditional Tamil Horoscope Writing (6-page booklet PDF)
  kp_astrology: boolean;      // KP Placidus, 249 Sub-Lords, Horary 1-249, 110 Events
  marriage_matching: boolean; // 10/12 Poruthams, 36 Guna Milan, Synastry
  panchang_muhurta: boolean;  // Live Panchang, Choghadiya, Gowri, Muhurta Finder
  numerology: boolean;        // Numerology Studio, Lo Shu, Name Correction, Vehicle/Mobile
  vastu: boolean;             // Vastu Shastra Assessment Engine
  remedies: boolean;          // Shastric Remedies & Navagraha Temples
  crm: boolean;               // Client CRM & Directory
  pdf_export: boolean;        // High-Resolution Vector PDF Generation
}

export interface UserSubscription {
  tier: SubscriptionTier;
  status: SubscriptionStatus;
  validUntil: string | null; // ISO timestamp string or null (lifetime/admin)
  maxPdfMonthly?: number;
}

export interface ModuleDefinition {
  key: PermissionKey;
  nameEn: string;
  nameTa: string;
  descriptionEn: string;
  descriptionTa: string;
  category: "core" | "regional" | "advanced" | "allied" | "management";
  iconName: string;
  routes: string[];
}

export const MODULE_REGISTRY: ModuleDefinition[] = [
  {
    key: "vedic",
    nameEn: "Parashari Vedic Astrology",
    nameTa: "வேத ஜோதிடம் & வர்க்கச் சக்கரங்கள்",
    descriptionEn: "Complete Parashari calculations, D1-D60 Vargas, Shadbala, Ashtakavarga, Yogas & Doshas",
    descriptionTa: "ராசி, நவாம்சம், ஷட்பலம், அஷ்டவர்க்கம், 60+ யோகங்கள் மற்றும் தோஷ ஆய்வுகள்",
    category: "core",
    iconName: "Compass",
    routes: ["/horoscope", "/tools/horoscope"],
  },
  {
    key: "tamil_horoscope",
    nameEn: "Traditional Tamil Horoscope Writing",
    nameTa: "பாரம்பரிய தமிழ் ஜாதகம் எழுதுதல்",
    descriptionEn: "Classical 6-page printable booklet with Tamil solar calendar, Nazhigai/Vinazhigai offsets & Graha Saram",
    descriptionTa: "தமிழ் வருட/மாத/நாழிகை கணக்கீட்டுடன் கூடிய அச்சிடத்தக்க 6-பக்க பாரம்பரிய ஜாதகப் புத்தகம்",
    category: "regional",
    iconName: "BookOpen",
    routes: ["/tools/horoscope-writing"],
  },
  {
    key: "kp_astrology",
    nameEn: "KP Astrology & Horary 1–249",
    nameTa: "உயர்நிலை கே.பி. & பிரசன்னம் 1–249",
    descriptionEn: "Placidus cusps, 249 sub-lords, 2,193 sub-sub-lords, ABCD significators, Horary and 110 life event analyzers",
    descriptionTa: "249 உப-அதிபதிகள், பாவக ஆரம்பங்கள், 1–249 பிரசன்ன ஜோதிடம் மற்றும் 110 நிகழ்வு கணிப்புகள்",
    category: "advanced",
    iconName: "Layers",
    routes: ["/tools/advanced-kp", "/tools/kp-events-prediction"],
  },
  {
    key: "marriage_matching",
    nameEn: "Marriage Compatibility & Porutham",
    nameTa: "திருமணப் பொருத்தம் & குண மிலான்",
    descriptionEn: "South Indian 10/12 Poruthams, North Indian 36 Guna Milan, Kuja dosha balance & Synastry",
    descriptionTa: "தென்னிந்திய 10/12 பொருத்தங்கள், வட இந்திய 36 குணங்கள் மற்றும் செவ்வாய் தோஷ சமநிலை",
    category: "core",
    iconName: "Heart",
    routes: ["/tools/marriage-prediction", "/tools/marriage-compatibility"],
  },
  {
    key: "panchang_muhurta",
    nameEn: "Daily Panchang & Auspicious Muhurta",
    nameTa: "தினசரி பஞ்சாங்கம் & சுப முகூர்த்தம்",
    descriptionEn: "5 Panchang limbs, Rahu Kalam, Yamagandam, Gowri Panchangam, Choghadiya & automated Muhurta finders",
    descriptionTa: "திதி, வாரம், நட்சத்திரம், யோகம், கரணம், கௌரி பஞ்சாங்கம் மற்றும் திருமண/கிரகப்பிரவேச முகூர்த்தங்கள்",
    category: "allied",
    iconName: "Calendar",
    routes: ["/muhurta"],
  },
  {
    key: "numerology",
    nameEn: "Numerology Studio & Name Correction",
    nameTa: "எண் கணித அரங்கம் & பெயர் திருத்தம்",
    descriptionEn: "Chaldean & Pythagorean systems, Lo Shu grid, Name correction, Vehicle & Mobile number harmony",
    descriptionTa: "கல்திய & பித்தகோரியன் முறைகள், லோ ஷு கிரிட், பெயர் திருத்தம், வண்டி மற்றும் மொபைல் எண் பகுப்பாய்வு",
    category: "allied",
    iconName: "Sparkles",
    routes: ["/tools/numerology"],
  },
  {
    key: "vastu",
    nameEn: "Vastu Shastra Assessment",
    nameTa: "வாஸ்து சாஸ்திர ஆய்வு",
    descriptionEn: "16-zone directional energy analysis, room-by-room compliance & elemental remediation",
    descriptionTa: "16 திசைகள் ஆற்றல் ஆய்வு, மனை/வீட்டு அறை அமைப்புகள் மற்றும் வாஸ்து பரிகாரங்கள்",
    category: "allied",
    iconName: "Home",
    routes: ["/vastu"],
  },
  {
    key: "remedies",
    nameEn: "Shastric Remedies & Navagraha Hub",
    nameTa: "பரிகாரங்கள் & நவகிரக ஆலயங்கள்",
    descriptionEn: "Comprehensive dosha remedies, stotras, gemstone guidance & verified Navagraha pilgrimage temples",
    descriptionTa: "சாஸ்திர பரிகாரங்கள், நவகிரக ஸ்தலங்கள், ரத்தினப் பரிந்துரைகள் மற்றும் மந்திரங்கள்",
    category: "allied",
    iconName: "Flame",
    routes: ["/remedies"],
  },
  {
    key: "crm",
    nameEn: "Astrologer CRM & Client Records",
    nameTa: "வாடிக்கையாளர் மேலாண்மை (CRM)",
    descriptionEn: "Multi-client directory, linked horoscopes, automated birthday alerts, and consultation notes",
    descriptionTa: "வாடிக்கையாளர் விபரங்கள், ஜாதகக் கோப்புகள், பிறந்தநாள் வாழ்த்து நினைவூட்டல் மற்றும் குறிப்புகள்",
    category: "management",
    iconName: "Users",
    routes: ["/customers"],
  },
  {
    key: "pdf_export",
    nameEn: "Publication PDF & Printing Rights",
    nameTa: "உயர் ரக பிடிஎஃப் அச்சிடும் உரிமை",
    descriptionEn: "Download and print vector 9-page Vedic reports and 6-page traditional Tamil booklets with custom headers",
    descriptionTa: "9-பக்க வேத அறிக்கை & 6-பக்க பாரம்பரிய தமிழ் ஜாதகப் புத்தகங்களை பிடிஎஃப் வடிவில் அச்சிடும் வசதி",
    category: "management",
    iconName: "FileDown",
    routes: ["/reports"],
  },
];

export const BASIC_PLAN_PERMISSIONS: UserPermissions = {
  vedic: true,
  tamil_horoscope: false,
  kp_astrology: false,
  marriage_matching: true,
  panchang_muhurta: true,
  numerology: false,
  vastu: false,
  remedies: true,
  crm: false,
  pdf_export: true,
};

export const PRO_PLAN_PERMISSIONS: UserPermissions = {
  vedic: true,
  tamil_horoscope: true,
  kp_astrology: true,
  marriage_matching: true,
  panchang_muhurta: true,
  numerology: true,
  vastu: true,
  remedies: true,
  crm: true,
  pdf_export: true,
};

export const TAMIL_SPECIALIST_PERMISSIONS: UserPermissions = {
  vedic: true,
  tamil_horoscope: true,
  kp_astrology: false,
  marriage_matching: true,
  panchang_muhurta: true,
  numerology: false,
  vastu: false,
  remedies: true,
  crm: true,
  pdf_export: true,
};

export const DEFAULT_PERMISSIONS: UserPermissions = PRO_PLAN_PERMISSIONS;

export const PLAN_PRESETS: Record<
  string,
  {
    nameEn: string;
    nameTa: string;
    tier: SubscriptionTier;
    monthlyPriceInr: number;
    yearlyPriceInr: number;
    permissions: UserPermissions;
    descriptionEn: string;
    descriptionTa: string;
  }
> = {
  basic: {
    nameEn: "Basic Astrologer (அடிப்படை)",
    nameTa: "அடிப்படை ஜோதிடர் திட்டம்",
    tier: "basic",
    monthlyPriceInr: 999,
    yearlyPriceInr: 9999,
    permissions: BASIC_PLAN_PERMISSIONS,
    descriptionEn: "Vedic charts, Panchang, Marriage Porutham, and basic PDF export",
    descriptionTa: "வேத ஜோதிடம், பஞ்சாங்கம், திருமணப் பொருத்தம், பரிகாரங்கள்",
  },
  tamil_specialist: {
    nameEn: "Tamil Horoscope Specialist (தமிழ் ஜாதகம்)",
    nameTa: "தமிழ் ஜாதகப் பிரதியாளர் திட்டம்",
    tier: "pro",
    monthlyPriceInr: 1999,
    yearlyPriceInr: 19999,
    permissions: TAMIL_SPECIALIST_PERMISSIONS,
    descriptionEn: "Vedic, Traditional Tamil 6-Page Booklet PDF Writing, Porutham, and Client CRM",
    descriptionTa: "வேத கணிப்பு, 6-பக்க பாரம்பரிய தமிழ் ஜாதகப் புத்தகம் எழுதுதல், பொருத்தம், CRM",
  },
  pro: {
    nameEn: "Pro / Commercial Studio (முழு ஜோதிட மையம்)",
    nameTa: "முழு தொழில்முறை ஜோதிட மையம்",
    tier: "pro",
    monthlyPriceInr: 2999,
    yearlyPriceInr: 29999,
    permissions: PRO_PLAN_PERMISSIONS,
    descriptionEn: "Complete suite: KP 249, Tamil Booklets, Numerology, Vastu, CRM, and Unlimited PDFs",
    descriptionTa: "அனைத்து அம்சங்களும்: கே.பி 249, தமிழ் ஜாதகம், எண் கணிதம், வாஸ்து, CRM, அளவற்ற பிடிஎஃப்",
  },
  enterprise: {
    nameEn: "Enterprise / White-Label (தனி பிராண்ட்)",
    nameTa: "முழு தனிப்பயன் பிராண்ட் திட்டம்",
    tier: "enterprise",
    monthlyPriceInr: 15000,
    yearlyPriceInr: 150000,
    permissions: PRO_PLAN_PERMISSIONS,
    descriptionEn: "Custom domain, personal brand logo, unlimited staff profiles, and priority updates",
    descriptionTa: "சொந்த டொமைன், சொந்த லோகோ, பல ஜோதிடர் கணக்குகள், முழு உரிமைகள்",
  },
};

/**
 * Checks if a given permission is active for the user.
 * - Admin always has full access.
 * - If account is suspended or expired, returns false.
 */
export function hasUserPermission(
  user: {
    role?: string;
    subscription?: UserSubscription;
    permissions?: Partial<UserPermissions>;
  } | null,
  key: PermissionKey
): boolean {
  if (!user) return false;
  if (user.role === "admin") return true;

  const sub = user.subscription;
  if (sub) {
    if (sub.status === "suspended") return false;
    if (sub.validUntil) {
      const expiry = new Date(sub.validUntil).getTime();
      if (!isNaN(expiry) && expiry < Date.now()) {
        return false;
      }
    }
  }

  // Check specific module permission flag
  return Boolean(user.permissions?.[key]);
}

/**
 * Checks if user's subscription is globally valid (not expired or suspended).
 */
export function isSubscriptionActive(
  user: {
    role?: string;
    subscription?: UserSubscription;
  } | null
): boolean {
  if (!user) return false;
  if (user.role === "admin") return true;

  const sub = user.subscription;
  if (!sub) return true;
  if (sub.status === "suspended") return false;
  if (sub.validUntil) {
    const expiry = new Date(sub.validUntil).getTime();
    if (!isNaN(expiry) && expiry < Date.now()) {
      return false;
    }
  }
  return true;
}
