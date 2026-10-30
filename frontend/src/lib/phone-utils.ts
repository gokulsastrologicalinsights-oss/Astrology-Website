/**
 * Phone Number Validation, Normalization, and WhatsApp Link Utilities
 * Gokul's Astrological Insights
 */

export interface CountryCodeOption {
  code: string; // e.g. "+91"
  name: string; // e.g. "India"
  flag: string; // e.g. "🇮🇳"
  example: string; // e.g. "98765 43210"
}

export const SUPPORTED_COUNTRY_CODES: CountryCodeOption[] = [
  { code: "+91", name: "India", flag: "🇮🇳", example: "98765 43210" },
  { code: "+1", name: "USA / Canada", flag: "🇺🇸", example: "202 555 0123" },
  { code: "+44", name: "United Kingdom", flag: "🇬🇧", example: "7911 123456" },
  { code: "+971", name: "UAE", flag: "🇦🇪", example: "50 123 4567" },
  { code: "+65", name: "Singapore", flag: "🇸🇬", example: "8123 4567" },
  { code: "+60", name: "Malaysia", flag: "🇲🇾", example: "12 345 6789" },
  { code: "+94", name: "Sri Lanka", flag: "🇱🇰", example: "71 234 5678" },
  { code: "+61", name: "Australia", flag: "🇦🇺", example: "412 345 678" },
  { code: "+49", name: "Germany", flag: "🇩🇪", example: "151 12345678" },
  { code: "+33", name: "France", flag: "🇫🇷", example: "6 12 34 56 78" },
];

export interface PhoneValidationResult {
  isValid: boolean;
  error?: string;
  nationalNumber: string;
  normalizedPhone: string; // E.164 with +, e.g. "+919876543210"
  whatsappNumber: string; // digits only, no +, e.g. "919876543210"
  displayPhone: string; // formatted for display, e.g. "+91 98765 43210"
}

/**
 * Strips all spaces, dashes, parentheses, dots, and formatting characters.
 */
export function cleanRawPhone(raw: string): string {
  if (!raw) return "";
  return raw.replace(/[\s\-\(\)\.]+/g, "").trim();
}

/**
 * Validates and normalizes a phone number for the selected country code.
 */
export function validateAndNormalizePhone(
  rawPhone: string,
  countryCode: string = "+91"
): PhoneValidationResult {
  const cleaned = cleanRawPhone(rawPhone);

  if (!cleaned) {
    return {
      isValid: false,
      error: "Customer WhatsApp number is required.",
      nationalNumber: "",
      normalizedPhone: "",
      whatsappNumber: "",
      displayPhone: "",
    };
  }

  const cleanCountryDigits = countryCode.replace(/\D/g, "");

  // If user included the country code in the input, strip it to extract the national number
  let digits = cleaned.replace(/\D/g, "");

  if (cleaned.startsWith("+")) {
    if (digits.startsWith(cleanCountryDigits)) {
      digits = digits.slice(cleanCountryDigits.length);
    }
  } else if (digits.startsWith(cleanCountryDigits) && digits.length > 10) {
    // e.g. "919876543210" -> "9876543210"
    digits = digits.slice(cleanCountryDigits.length);
  }

  // Remove single leading zero if entered (e.g. 09876543210)
  if (digits.startsWith("0") && digits.length > 9) {
    digits = digits.slice(1);
  }

  // Country-specific validations
  if (countryCode === "+91") {
    // India: 10 digits starting with 6, 7, 8, or 9
    if (!/^[6-9]\d{9}$/.test(digits)) {
      let specificError = "Please enter a valid 10-digit Indian mobile number.";
      if (digits.length !== 10) {
        specificError = `Indian mobile number must be exactly 10 digits (entered ${digits.length}).`;
      } else if (!/^[6-9]/.test(digits)) {
        specificError = "Indian mobile numbers must start with 6, 7, 8, or 9.";
      }
      return {
        isValid: false,
        error: specificError,
        nationalNumber: digits,
        normalizedPhone: "",
        whatsappNumber: "",
        displayPhone: "",
      };
    }

    const normalized = `+91${digits}`;
    const wa = `91${digits}`;
    const display = `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`;
    return {
      isValid: true,
      nationalNumber: digits,
      normalizedPhone: normalized,
      whatsappNumber: wa,
      displayPhone: display,
    };
  }

  if (countryCode === "+1") {
    // US/Canada: 10 digits starting with 2-9
    if (!/^[2-9]\d{9}$/.test(digits)) {
      return {
        isValid: false,
        error: "US/Canada phone number must be 10 digits with a valid area code (2-9).",
        nationalNumber: digits,
        normalizedPhone: "",
        whatsappNumber: "",
        displayPhone: "",
      };
    }
    const normalized = `+1${digits}`;
    const wa = `1${digits}`;
    const display = `+1 (${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    return {
      isValid: true,
      nationalNumber: digits,
      normalizedPhone: normalized,
      whatsappNumber: wa,
      displayPhone: display,
    };
  }

  if (countryCode === "+44") {
    // UK: 10 to 11 digits
    if (!/^\d{10,11}$/.test(digits)) {
      return {
        isValid: false,
        error: "UK phone number must be 10 or 11 digits.",
        nationalNumber: digits,
        normalizedPhone: "",
        whatsappNumber: "",
        displayPhone: "",
      };
    }
    const normalized = `+44${digits}`;
    const wa = `44${digits}`;
    const display = `+44 ${digits.slice(0, 4)} ${digits.slice(4)}`;
    return {
      isValid: true,
      nationalNumber: digits,
      normalizedPhone: normalized,
      whatsappNumber: wa,
      displayPhone: display,
    };
  }

  // Generic international validation: 7 to 15 digits
  if (!/^\d{7,15}$/.test(digits)) {
    return {
      isValid: false,
      error: `Phone number must be between 7 and 15 digits for ${countryCode}.`,
      nationalNumber: digits,
      normalizedPhone: "",
      whatsappNumber: "",
      displayPhone: "",
    };
  }

  const normalized = `${countryCode}${digits}`;
  const wa = `${cleanCountryDigits}${digits}`;
  const display = `${countryCode} ${digits}`;
  return {
    isValid: true,
    nationalNumber: digits,
    normalizedPhone: normalized,
    whatsappNumber: wa,
    displayPhone: display,
  };
}

/**
 * Returns the plain-text birthday wish message for the specified recipient and language.
 */
export function getBirthdayWishMessageText(
  customerName?: string | null,
  lang: "en" | "ta" = "ta"
): string {
  const trimmedName = (customerName || "").trim();
  const safeName = trimmedName || (lang === "ta" ? "அன்பரே" : "Valued Client");

  return lang === "ta"
    ? `வணக்கம் ${safeName} ❤️

உங்களுக்கு எங்களின் இனிய பிறந்தநாள் நல்வாழ்த்துகள்! 🎉🎂

இந்தப் புதிய ஆண்டு உங்கள் வாழ்வில் **நல்ல ஆரோக்கியம், மனநிம்மதி, மகிழ்ச்சி, செல்வச் செழிப்பு** என அனைத்து நலன்களையும் அள்ளித் தரட்டும். இறைவனின் திருவருளால் உங்கள் எண்ணங்கள் அனைத்தும் ஈடேறி, வாழ்க்கை முழுவதும் வெற்றியும் சந்தோஷமும் நிறைந்திருக்க மனதார வாழ்த்துகிறோம்! 🙏✨

🎁 **உங்களுக்காக எங்களின் சிறப்புப் பிறந்தநாள் பரிசு!** 🔮(Free Astrology Consultation)

எங்களின் ஜோதிடச் சேவையைப் பயன்படுத்திய அனுபவம் உங்களுக்குப் பிடித்திருந்தால், Google-ல் ⭐⭐⭐⭐⭐ 5-Star Review வழங்கி, உங்களின் அன்பான ஆதரவிற்கு நன்றியாக, **எங்களிடமிருந்து ஒரு இலவச ஜோதிட ஆலோசனை (Free Astrology Consultation) பெற்றுக்கொள்ளுங்கள்!** ❤️

⭐ **Google Review வழங்க:**
https://share.google/iwcotLgirm9CMBQsu

மீண்டும் ஒருமுறை இனிய பிறந்தநாள் வாழ்த்துகள்! 💐

உங்கள் வாழ்க்கையில் ஒவ்வொரு நாளும் புதிய நம்பிக்கையும், மகிழ்ச்சியும், வெற்றியும் மலரட்டும்! ❤️

அன்புடன்,
**கோகுல் முருகன்**
*Gokul’s Astrological Insights* 🔱`
    : `Hello ${safeName} ❤️

Wishing you our warmest Happy Birthday! 🎉🎂

May this new year bring **good health, peace of mind, happiness, and prosperity** into your life in abundance. With divine blessings, may all your aspirations come true, and we wholeheartedly wish your life be filled with success and happiness! 🙏✨

🎁 **A Special Birthday Gift For You!** 🔮(Free Astrology Consultation)

If you enjoyed our astrological services, kindly leave a ⭐⭐⭐⭐⭐ 5-Star Review on Google, and as a token of gratitude for your loving support, receive a **Free Astrology Consultation from us!** ❤️

⭐ **To leave a Google Review:**
https://share.google/iwcotLgirm9CMBQsu

Once again, Happy Birthday! 💐

May every day in your life blossom with renewed hope, joy, and success! ❤️

Warm regards,
**Gokul Murugan**
*Gokul’s Astrological Insights* 🔱`;
}

/**
 * Generates an authentic WhatsApp click-to-chat link with personalized birthday message.
 * Strict requirement: Use the international number format in the WhatsApp link,
 * without the leading plus sign, spaces, or punctuation.
 * Never generate a WhatsApp URL for an empty or invalid number.
 */
export function generateWhatsAppBirthdayLink(
  whatsappNumber?: string | null,
  customerName?: string | null,
  lang: "en" | "ta" = "ta"
): string {
  if (!whatsappNumber) return "";

  // Strip any accidental leading plus or spaces
  const cleanWaNumber = whatsappNumber.replace(/\D/g, "");
  if (!cleanWaNumber || cleanWaNumber.length < 7) {
    return "";
  }

  const messageText = getBirthdayWishMessageText(customerName, lang);
  const encodedText = encodeURIComponent(messageText);
  // Using direct api.whatsapp.com/send/ endpoint instead of wa.me shortlink.
  // wa.me's HTTP 302 redirect has a known server-side bug that corrupts 4-byte UTF-8 emojis into %EF%BF%BD (diamond replacement characters).
  return `https://api.whatsapp.com/send/?phone=${cleanWaNumber}&text=${encodedText}`;
}

/**
 * Checks whether a given birth date (YYYY-MM-DD) falls on today's date in the Asia/Kolkata timezone.
 */
export function isBirthdayTodayInKolkata(birthDateStr?: string | null): boolean {
  if (!birthDateStr) return false;

  // Extract month and day from birthDateStr (supports YYYY-MM-DD)
  const parts = birthDateStr.split("-");
  if (parts.length < 3) return false;
  const birthMonth = parseInt(parts[1], 10);
  const birthDay = parseInt(parts[2], 10);

  if (isNaN(birthMonth) || isNaN(birthDay)) return false;

  // Current date in Asia/Kolkata
  const now = new Date();
  const kolkataFormatter = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Kolkata",
    month: "numeric",
    day: "numeric",
  });

  const formatted = kolkataFormatter.format(now); // e.g. "10/18" (month/day)
  const [currMonthStr, currDayStr] = formatted.split("/");
  const currMonth = parseInt(currMonthStr, 10);
  const currDay = parseInt(currDayStr, 10);

  return birthMonth === currMonth && birthDay === currDay;
}

/**
 * Returns today's formatted date string in Asia/Kolkata (YYYY-MM-DD).
 */
export function getTodayKolkataDateString(): string {
  const now = new Date();
  const kolkataFormatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Kolkata",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  return kolkataFormatter.format(now); // "YYYY-MM-DD"
}
