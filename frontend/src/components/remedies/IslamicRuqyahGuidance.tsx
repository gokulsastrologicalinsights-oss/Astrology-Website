"use client";

import React, { useState } from "react";
import { useLanguage } from "@/lib/i18n";
import {
  ShieldCheck,
  AlertTriangle,
  BookOpen,
  Droplets,
  HeartHandshake,
  CheckCircle2,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  Moon,
  Sun,
  Flame,
  Info,
  Sparkles,
  ExternalLink,
} from "lucide-react";

interface IslamicRuqyahGuidanceProps {
  initialOpen?: boolean;
  compact?: boolean;
}

export function IslamicRuqyahGuidance({
  initialOpen = false,
  compact = false,
}: IslamicRuqyahGuidanceProps) {
  const { language } = useLanguage();
  const isTa = language === "ta";

  const [isOpen, setIsOpen] = useState(initialOpen);
  const [activeTab, setActiveTab] = useState<
    "ruling" | "sidr_ruqyah" | "daily_armor" | "quranic_verses" | "disenchantment"
  >("sidr_ruqyah");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (key: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  return (
    <div className="rounded-2xl border-2 border-emerald-300 bg-gradient-to-br from-emerald-50/80 via-white to-teal-50/50 shadow-xs overflow-hidden transition-all">
      {/* Header Bar */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-4 sm:p-5 cursor-pointer bg-emerald-900 text-white select-none hover:bg-emerald-950 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-800/80 border border-emerald-600/50 flex items-center justify-center shrink-0 shadow-inner">
            <Moon className="w-5 h-5 text-amber-300" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider bg-emerald-700/80 text-emerald-100 border border-emerald-500/40">
                {isTa ? "இஸ்லாமிய ஷரீஆ வழிகாட்டல்" : "Islamic Shariah Treatise"}
              </span>
              <span className="text-[11px] text-emerald-200 font-medium">
                {isTa
                  ? "அஷ்ஷெய்க் பின் பாஸ் (ரஹிமஹுல்லாஹ்)"
                  : "Grand Mufti Sheikh Ibn Baz (Rahimahullah)"}
              </span>
            </div>
            <h3 className="font-extrabold text-sm sm:text-base text-white mt-0.5 flex items-center gap-1.5">
              <span>
                {isTa
                  ? "சூனியம் மற்றும் சோதிடம் குறித்த இஸ்லாமிய சட்ட விளக்கம் & ருக்யா நிவாரணம்"
                  : "Islamic Legal Rulings on Magic, Astrology & Authentic Sunnah Ruqyah"}
              </span>
            </h3>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-block text-xs font-semibold text-emerald-200">
            {isOpen
              ? isTa
                ? "சுருக்குக"
                : "Hide Guide"
              : isTa
              ? "விளக்கம் காண்க"
              : "View Guide"}
          </span>
          <div className="p-1 rounded-lg bg-emerald-800 text-emerald-100">
            {isOpen ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </div>
        </div>
      </div>

      {/* Expandable Body */}
      {isOpen && (
        <div className="p-4 sm:p-6 space-y-6 text-slate-800">
          {/* Treatise Citation Banner */}
          <div className="p-3.5 rounded-xl bg-emerald-100/70 border border-emerald-300/80 flex items-start gap-3 text-xs leading-relaxed">
            <Info className="w-5 h-5 text-emerald-800 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-emerald-950">
                {isTa
                  ? "ஆதார நூல்: 'சூனியம் மற்றும் சோதிடம் குறித்த இஸ்லாமிய சட்ட விளக்கம்'"
                  : "Source: 'Islamic Legal Clarification Regarding Black Magic and Astrology'"}
              </p>
              <p className="text-emerald-900 mt-0.5">
                {isTa
                  ? "சஊதி அரேபியாவின் முன்னாள் தலைமை முஃப்தி அஷ்ஷெய்க் அப்துல் அஸீஸ் இப்னு பாஸ் (ரஹ்) அவர்களின் பத்வா மற்றும் வழிகாட்டலின்படி, சோதிடர்களிடம் செல்வது தடைசெய்யப்பட்டாலும், செய்வினை/சூனியம் மற்றும் கண் திருஷ்டியால் பாதிக்கப்பட்டோர் அல்குர்ஆன் மற்றும் சுன்னத்தான திக்ருகள் (ருக்யா ஷரீஆ) மூலம் நிவாரணம் பெறலாம்."
                  : "Compiled from the authoritative rulings of Grand Mufti Sheikh Abdul Aziz ibn Abdullah ibn Baz. While seeking soothsayers is strictly prohibited, victims of witchcraft, evil eye, and marital estrangement have complete healing through Quranic Ruqyah and Prophetic supplications."}
              </p>
            </div>
          </div>

          {/* Sub Navigation Tabs */}
          <div className="flex items-center gap-1.5 p-1.5 rounded-xl bg-slate-100 border border-slate-200 overflow-x-auto text-xs">
            <button
              type="button"
              onClick={() => setActiveTab("sidr_ruqyah")}
              className={`px-3 py-2 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer ${
                activeTab === "sidr_ruqyah"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <Droplets className="w-3.5 h-3.5" />
              <span>{isTa ? "7 பச்சை இலந்தை இலை சிகிச்சை" : "7 Sidr Leaves Cure"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("ruling")}
              className={`px-3 py-2 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer ${
                activeTab === "ruling"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{isTa ? "மார்க்கத் தீர்ப்பு & எச்சரிக்கை" : "Shariah Rulings & Hadiths"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("quranic_verses")}
              className={`px-3 py-2 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer ${
                activeTab === "quranic_verses"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>{isTa ? "சூனியம் முறிக்கும் குர்ஆன் ஆயத்துக்கள்" : "Magic-Destroying Verses"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("daily_armor")}
              className={`px-3 py-2 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer ${
                activeTab === "daily_armor"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>{isTa ? "தினசரி தற்காப்பு அரண்" : "Daily Protection Fortress"}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab("disenchantment")}
              className={`px-3 py-2 rounded-lg font-bold transition-all whitespace-nowrap flex items-center gap-1.5 cursor-pointer ${
                activeTab === "disenchantment"
                  ? "bg-emerald-700 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-white/60"
              }`}
            >
              <Flame className="w-3.5 h-3.5" />
              <span>{isTa ? "முடிச்சுகளை அழித்தல் & தாம்பத்தியம்" : "Disenchantment & Marital Discord"}</span>
            </button>
          </div>

          {/* TAB 1: 7 Sidr Leaves Ruqyah Cure */}
          {activeTab === "sidr_ruqyah" && (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white border border-emerald-200 shadow-2xs space-y-3">
                <div className="flex items-center justify-between border-b border-emerald-100 pb-2">
                  <h4 className="font-extrabold text-sm sm:text-base text-emerald-950 flex items-center gap-2">
                    <Droplets className="w-4 h-4 text-emerald-600" />
                    <span>
                      {isTa
                        ? "ஷரீஆ அனுமதித்த 7 பச்சை இலந்தை இலை ருக்யா சிகிச்சை முறை"
                        : "7 Green Sidr (Lote) Leaves Sunnah Ruqyah Water Treatment"}
                    </span>
                  </h4>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    {isTa ? "சுன்னத்தான அருமருந்து" : "Sunnah Remedy"}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed">
                  {isTa
                    ? "சூனியத்தினால் பாதிக்கப்பட்டோர், கண் திருஷ்டி அல்லது தாம்பத்திய உறவில் ஈடுபட முடியாமல் செய்வினையால் முடக்கப்பட்டோருக்கு (கட்டுப்பாடு) அறிஞர்கள் வஹ்ப் இப்னு முனப்பஹ், இப்னுல் கைய்யிம் மற்றும் அஷ்ஷெய்க் இப்னு பாஸ் (ரஹ்) பரிந்துரைத்த மிகச்சிறந்த சிகிச்சை:"
                    : "Endorsed by early scholars Wahb ibn Munabbih, Ibn al-Qayyim, and Grand Mufti Sheikh Ibn Baz as a decisive remedy for black magic, evil eye, and marital separation spells:"}
                </p>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200/80">
                    <strong className="text-emerald-950 block mb-1 font-extrabold">
                      {isTa ? "படி 1: தயாரிப்பு (இலை அரைத்தல்)" : "Step 1: Preparation (Crushing Sidr Leaves)"}
                    </strong>
                    <p className="text-slate-700">
                      {isTa
                        ? "இலந்தை மரத்தின் (Sidr / Lote tree / Ziziphus) ஏழு பச்சை இலைகளைப் பறித்து இரு கற்களுக்கிடையே அல்லது சுத்தமான உரலில் நன்கு அரைத்துக் கொள்ளவும்."
                        : "Pick 7 fresh green leaves of the Sidr (Lote) tree and crush them finely between two clean stones or with a pestle."}
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200/80">
                    <strong className="text-emerald-950 block mb-1 font-extrabold">
                      {isTa ? "படி 2: நீரில் கலக்குதல்" : "Step 2: Mixing into Water"}
                    </strong>
                    <p className="text-slate-700">
                      {isTa
                        ? "அரைத்த இலந்தை இலை விழுதை ஒரு பாத்திரத்தில் இட்டு குடிப்பதற்கும் உடல் முழுவதும் குளிப்பதற்கும் (குஸ்ல்) போதுமான சுத்தமான நீரை அதில் ஊற்றவும்."
                        : "Place the crushed leaves into a clean vessel and pour in water sufficient for drinking 3 sips and performing a full purifying bath (Ghusl)."}
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200/80">
                    <strong className="text-emerald-950 block mb-1 font-extrabold">
                      {isTa ? "படி 3: அல்குர்ஆன் மற்றும் துஆக்களை ஓதுதல்" : "Step 3: Reciting Ruqyah into the Water"}
                    </strong>
                    <p className="text-slate-700">
                      {isTa
                        ? "சுத்தமாக உளூச் செய்து, பாத்திரத்தின் நீருக்கு அருகில் வாயை வைத்து பின்வரும் ஸூராக்களையும் ஆயத்துக்களையும் நபிகளாரின் துஆக்களையும் ஓதி அவ்வப்போது நீரில் மென்மையாக ஊதவும்:"
                        : "Perform ritual ablution (Wudu), bring the water close to your mouth, and recite the following while gently blowing into the water:"}
                    </p>
                    <ul className="list-disc list-inside mt-2 space-y-1 text-slate-800 font-medium pl-2">
                      <li>{isTa ? "ஸூறதுல் பாத்திஹா (அல்-ஹம்து ஸூரா) - 1 முறை" : "Surah Al-Fatihah (1 time)"}</li>
                      <li>{isTa ? "ஆயதுல் குர்ஸி (ஸூறதுல் பகரா: 255) - 1 முறை" : "Ayatul Kursi (Surah Al-Baqarah: 255 - 1 time)"}</li>
                      <li>{isTa ? "ஸூறதுல் காஃபிரூன் - 1 முறை" : "Surah Al-Kafirun (1 time)"}</li>
                      <li>{isTa ? "ஸூறதுல் இஹ்லாஸ் (குல்ஹுவல்லாஹு அஹத்) - 3 முறை" : "Surah Al-Ikhlas (3 times)"}</li>
                      <li>{isTa ? "ஸூறதுல் பலக் (குல்அஊது பிரப்பில் பலக்) - 3 முறை" : "Surah Al-Falaq (3 times)"}</li>
                      <li>{isTa ? "ஸூறதுந் நாஸ் (குல்அஊது பிரப்பின்னாஸ்) - 3 முறை" : "Surah An-Nas (3 times)"}</li>
                      <li>
                        {isTa
                          ? "மூஸா (அலை) அவர்கள் பிர்அவ்னின் சூனியத்தை முறியடித்த வசனங்கள் (ஸூறா அல்-அஃராப் 7:117-119, ஸூறா யூனுஸ் 10:79-82, ஸூறா தாஹா 20:65-69)"
                          : "The Moses magic-destroying verses (Surah Al-A'raf 7:117-119, Surah Yunus 10:79-82, Surah Ta-Ha 20:65-69)"}
                      </li>
                      <li>
                        {isTa
                          ? "நபியவர்களின் நோய் நிவாரண துஆ: 'அல்லாஹும்ம ரப்பன் நாஸி அத்ஹிபில் பஃஸ வஷ்ஃபி அன்தஷ் ஷாஃபி...' - 3 முறை"
                          : "Prophetic Healing Dua: 'Allahumma Rabban-naas adhhibil-ba'sa washfi Antash-Shaafee...' - 3 times"}
                      </li>
                      <li>
                        {isTa
                          ? "ஜிப்ரீல் (அலை) ஓதிய ருக்யா துஆ: 'பிஸ்மில்லாஹி அர்கீக மின் குல்லி ஷைய்இன் யுஃதீக...' - 3 முறை"
                          : "Jibril's Ruqyah Dua: 'Bismillahi arqeeka min kulli shay'in yu'dheeka...' - 3 times"}
                      </li>
                    </ul>
                  </div>

                  <div className="p-3 rounded-lg bg-emerald-50/60 border border-emerald-200/80">
                    <strong className="text-emerald-950 block mb-1 font-extrabold">
                      {isTa ? "படி 4: அருந்துதல் & குளித்தல்" : "Step 4: Drinking and Bathing (Ghusl)"}
                    </strong>
                    <p className="text-slate-700">
                      {isTa
                        ? "ஓதிய நீரிலிருந்து மூன்று மிடர்கள் குடித்துவிட்டு, எஞ்சிய நீரைக் கொண்டு உடல் முழுவதும் குளிக்க வேண்டும் (பாத்ரூமில் குளிக்காமல் சுத்தமான இடத்தில் குளித்து அந்த தண்ணீரை செடி கொடிகளுக்கு ஊற்றுவது சிறப்பு). நோய் குணமாகும் வரை பல நாட்கள் செய்யலாம்."
                        : "Drink 3 sips of the recited water, then wash and bathe (ghusl) with the rest. Repeat daily until symptoms completely subside."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Shariah Rulings & Hadiths */}
          {activeTab === "ruling" && (
            <div className="space-y-4 text-xs">
              {/* Core Warning */}
              <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 space-y-2">
                <div className="flex items-center gap-2 font-extrabold text-rose-950 text-sm">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  <span>{isTa ? "சோதிடர்களிடம் செல்லுதல் & சூனியம் குறித்த இஸ்லாமிய சட்டம்" : "Prohibition of Astrologers & Sorcery in Islam"}</span>
                </div>
                <p className="text-rose-900 leading-relaxed">
                  {isTa
                    ? "மறைவானவற்றின் ஞானம் ('இல்முல் ஃகைப்') அல்லாஹ் ஒருவனுக்கே உரியது. 'வானங்களிலும் பூமியிலும் உள்ள மறைவானவற்றை அல்லாஹ்வைத் தவிர வேறு யாரும் அறியமாட்டார்' (ஸூறா அந்-நம்ல் 27:65). எனவே மறைவானதை அறிவதாக வாதிடும் ஜோதிடர்கள், குறிசொல்வோர், மந்திரவாதிகளிடம் சென்று விசாரிப்பதும் அவர்கள் கூறுவதை நம்புவதும் இஸ்லாத்தில் மிகக் கடுமையான பாவமாகும்."
                    : "Knowledge of the unseen ('Ilm al-Ghayb) belongs solely to Allah (Surah An-Naml 27:65). Claiming or consulting astrologers, soothsayers, or fortune-tellers who allege knowledge of the unseen is categorized as Kufr (disbelief) and Shirk."}
                </p>
              </div>

              {/* Hadith Cards */}
              <div className="space-y-3">
                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-emerald-900 text-[11px] uppercase tracking-wide">
                      {isTa ? "1. நாற்பது நாட்களின் தொழுகை மறுக்கப்படுதல்" : "1. 40 Days of Unaccepted Prayers"}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold">Sahih Muslim 2230</span>
                  </div>
                  <p className="font-arabic text-sm text-right text-emerald-950 font-semibold" dir="rtl">
                    «مَنْ أَتَى عَرَّافًا فَسَأَلَهُ عَنْ شَيْءٍ لَمْ تُقْبَلْ لَهُ صَلَاةٌ أَرْبَعِينَ لَيْلَةً»
                  </p>
                  <p className="text-slate-800 font-medium">
                    {isTa
                      ? "நபிகள் நாயகம் (ஸல்) கூறினார்கள்: 'யார் (சோதிடன்) குறி சொல்பவனிடம் சென்று ஏதேனும் ஒன்றைப் பற்றி விசாரித்தால் அவனுடைய நாற்பது நாட்களின் தொழுகைகள் ஏற்றுக் கொள்ளப்படமாட்டாது.'"
                      : "The Prophet (pbuh) said: 'Whoever visits a fortune teller or astrologer and asks him about anything, his prayer will not be accepted for forty nights.'"}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-emerald-900 text-[11px] uppercase tracking-wide">
                      {isTa ? "2. முஹம்மத் (ஸல்) மீது அருளப்பட்டதை நிராகரித்தல்" : "2. Disbelief in Divine Revelation"}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold">Abu Dawud 3904 / Musnad Ahmad</span>
                  </div>
                  <p className="font-arabic text-sm text-right text-emerald-950 font-semibold" dir="rtl">
                    «مَنْ أَتَى كَاهِنًا أَوْ عَرَّافًا فَصَدَّقَهُ بِمَا يَقُولُ فَقَدْ كَفَرَ بِمَا أُنْزِلَ عَلَى مُحَمَّدٍ»
                  </p>
                  <p className="text-slate-800 font-medium">
                    {isTa
                      ? "நபிகள் நாயகம் (ஸல்) கூறினார்கள்: 'யார் ஒரு சோதிடனிடம் அல்லது குறிசொல்பவரிடம் சென்று அவன் சொல்வதை நம்பி உண்மைப்படுத்துகிறாரோ, அவர் முஹம்மத் (ஸல்) அவர்களின் மீது இறக்கியருளப்பட்டதை நிராகரித்தவராவார்.'"
                      : "The Prophet (pbuh) said: 'Whoever goes to a soothsayer or an astrologer and believes in what he says has disbelieved in that which was revealed to Muhammad (pbuh).'"}
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-white border border-slate-200 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="font-extrabold text-emerald-900 text-[11px] uppercase tracking-wide">
                      {isTa ? "3. எங்களைச் சார்ந்தவரல்ல" : "3. Not of Us"}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold">Musnad Al-Bazzar</span>
                  </div>
                  <p className="font-arabic text-sm text-right text-emerald-950 font-semibold" dir="rtl">
                    «لَيْسَ مِنَّا مَنْ تَطَيَّرَ أَوْ تُطُيِّرَ لَهُ أَوْ تَكَهَّنَ أَوْ تُكُهِّنَ لَهُ أَوْ سَحَرَ أَوْ سُحِرَ لَهُ»
                  </p>
                  <p className="text-slate-800 font-medium">
                    {isTa
                      ? "நபிகள் நாயகம் (ஸல்) கூறினார்கள்: 'சகுனம் பார்ப்பவரும் தனக்கு பார்க்குமாறு சொல்பவரும், சோதிடம் பார்ப்பவரும் பார்த்து விடுமாறு சொல்பவரும், சூனியம் செய்பவரும் சூனியம் செய்யுமாறு வேண்டுபவரும் எங்களைச் சார்ந்தவரல்ல.'"
                      : "The Prophet (pbuh) said: 'He is not of us who seeks omens or has them sought for him, or who tells fortunes or has his fortune told, or who practices sorcery or has sorcery practiced for him.'"}
                  </p>
                </div>
              </div>

              {/* Forbidden Treatments */}
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-2">
                <h5 className="font-extrabold text-amber-950">
                  {isTa ? "விலக்கப்பட்ட சிகிச்சை முறைகள் (நுஷ்ரா & ஷைத்தானிய ஏமாற்று வித்தைகள்):" : "Forbidden Treatment Methods (Nushrah & Demonic Practices):"}
                </h5>
                <ul className="list-disc list-inside space-y-1 text-amber-900">
                  <li>
                    {isTa
                      ? "சூனியத்தை அழிக்க மற்றொரு மந்திரவாதியிடம் செல்லுதல் ('நுஷ்ரா' ஷைத்தானின் செயல் என நபியவர்கள் தடைசெய்துள்ளார்கள்)."
                      : "Consulting another magician or sorcerer to undo magic (Nushrah via devils is forbidden)."}
                  </li>
                  <li>
                    {isTa
                      ? "ஜின்களுக்கு ஆடு, கோழி பலியிட்டு இரத்தம் சிந்துதல் அல்லது அல்லாஹ் அல்லாதவர்களிடம் உதவி கோருதல் (அஷ்ஷிர்குல் அக்பர்)."
                      : "Animal sacrifice to jinns or invoking unseen spirits (Ash-Shirk al-Akbar)."}
                  </li>
                  <li>
                    {isTa
                      ? "தாயத்து தகடுகளில் புரியாத எண்கள், கட்டங்கள், மந்திரக் கோடுகள் வரைந்து உடலில் கட்டுதல்."
                      : "Wearing amulets, talismans with occult numerical squares, demonic sigils, or knotted strings."}
                  </li>
                  <li>
                    {isTa
                      ? "நோயாளியிடம் தாயார் பெயர், உறவினர் பெயர்களைக் கேட்டு ஜின்களை வரவழைத்து சிகிச்சை செய்தல்."
                      : "Asking for the patient's mother's name to invoke jinn or divine occult matters."}
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* TAB 3: Magic-Destroying Quranic Verses */}
          {activeTab === "quranic_verses" && (
            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-950">
                <p className="font-semibold">
                  {isTa
                    ? "மூஸா (அலை) அவர்கள் பிர்அவ்னின் சூனியக்காரர்களை முறியடித்த பின்வரும் மூன்று அத்தியாயங்களின் வசனங்களை 7 இலந்தை இலை நீரில் ஓதுவது சூனியத்தை வேரறுக்கும் என அஷ்ஷெய்க் இப்னு பாஸ் குறிப்பிடுகிறார்:"
                    : "The 3 historical Quranic passages where Prophet Moses extinguished Pharaoh's sorcery, prescribed by Sheikh Ibn Baz to recite over Ruqyah water:"}
                </p>
              </div>

              {/* Surah Al-A'raf 7:117-119 */}
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-emerald-900">1. ஸூறா அல்-அஃராப் (7: 117-119)</span>
                  <button
                    type="button"
                    onClick={() =>
                      handleCopy(
                        "araf",
                        "وَأَوْحَيْنَا إِلَىٰ مُوسَىٰ أَنْ أَلْقِ عَصَاكَ ۖ فَإِذَا هِيَ تَلْقَفُ مَا يَأْفِكُونَ ۝ فَوَقَعَ الْحَقُّ وَبَطَلَ مَا كَانُوا يَعْمَلُونَ ۝ فَغُلِبُوا هُنَالِكَ وَانقَلَبُوا صَاغِرِينَ"
                      )
                    }
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 hover:text-emerald-900"
                  >
                    {copiedKey === "araf" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === "araf" ? (isTa ? "நகலெடுக்கப்பட்டது" : "Copied") : isTa ? "நகல்" : "Copy"}</span>
                  </button>
                </div>
                <p className="font-arabic text-base text-right leading-loose text-slate-900" dir="rtl">
                  ۞ وَأَوْحَيْنَا إِلَىٰ مُوسَىٰ أَنْ أَلْقِ عَصَاكَ ۖ فَإِذَا هِيَ تَلْقَفُ مَا يَأْفِكُونَ ۝ فَوَقَعَ الْحَقُّ وَبَطَلَ مَا كَانُوا يَعْمَلُونَ ۝ فَغُلِبُوا هُنَالِكَ وَانقَلَبُوا صَاغِرِينَ ۝
                </p>
                <p className="text-slate-600 italic">
                  வஅவ்ஹைனா இலா மூஸா அன் அல்கி அஸாக ஃபஇஃதா ஹிய தல்ஃகஃபு மா யஃபிகூன், ஃப வகஅல்ஹக்கு வபதல மா கானூ யஃமலூன், ஃபஃகுலிபூ ஹுனாலிக வன் கலபூ ஸாஃகிரீன்.
                </p>
                <p className="text-slate-800">
                  {isTa
                    ? "பொருள்: 'உமது கைத்தடியை போடும்' என மூஸாவுக்கு நாம் வஹி அறிவித்தோம். அவர் அதனைக் கீழே போட்டதும் அது அவர்கள் பாம்பாக கற்பனை செய்தவற்றை விழுங்கிவிட்டது. உண்மை தெளிவாகிவிட்டது! அவர்கள் செய்துகொண்டிருந்தவை வீணாகிவிட்டன. அதனால் அவர்கள் அங்கே தோற்கடிக்கப்பட்டு சிறுமையடைந்தவர்களாகத் திரும்பிச்சென்றார்கள்."
                    : "Meaning: And We inspired to Moses: 'Throw your staff,' and at once it devoured what they were falsifying. So the truth was established, and that which they were doing was made void. And they were vanquished there and were made small."}
                </p>
              </div>

              {/* Surah Yunus 10:79-82 */}
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-emerald-900">2. ஸூறா யூனுஸ் (10: 79-82)</span>
                  <button
                    type="button"
                    onClick={() =>
                      handleCopy(
                        "yunus",
                        "وَقَالَ فِرْعَوْنُ ائْتُونِي بِكُلِّ سَاحِرٍ عَلِيمٍ ۝ فَلَمَّا جَاءَ السَّحَرَةُ قَالَ لَهُم مُّوسَىٰ أَلْقُوا مَا أَنتُم مُّلْقُونَ ۝ فَلَمَّا أَلْقَوْا قَالَ مُوسَىٰ مَا جِئْتُم بِهِ السِّحْرُ ۖ إِنَّ اللَّهَ سَيُبْطِلُهُ ۖ إِنَّ اللَّهَ لَا يُصْلِحُ عَمَلَ الْمُفْسِدِينَ ۝ وَيُحِقُّ اللَّهُ الْحَقَّ بِكَلِمَاتِهِ وَلَوْ كَرِهَ الْمُجْرِمُونَ"
                      )
                    }
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 hover:text-emerald-900"
                  >
                    {copiedKey === "yunus" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === "yunus" ? (isTa ? "நகலெடுக்கப்பட்டது" : "Copied") : isTa ? "நகல்" : "Copy"}</span>
                  </button>
                </div>
                <p className="font-arabic text-base text-right leading-loose text-slate-900" dir="rtl">
                  وَقَالَ فِرْعَوْنُ ائْتُونِي بِكُلِّ سَاحِرٍ عَلِيمٍ ۝ فَلَمَّا جَاءَ السَّحَرَةُ قَالَ لَهُم مُّوسَىٰ أَلْقُوا مَا أَنتُم مُّلْقُونَ ۝ فَلَمَّا أَلْقَوْا قَالَ مُوسَىٰ مَا جِئْتُم بِهِ السِّحْرُ ۖ إِنَّ اللَّهَ سَيُبْطِلُهُ ۖ إِنَّ اللَّهَ لَا يُصْلِحُ عَمَلَ الْمُفْسِدِينَ ۝ وَيُحِقُّ اللَّهُ الْحَقَّ بِكَلِمَاتِهِ وَلَوْ كَرِهَ الْمُجْرِمُونَ ۝
                </p>
                <p className="text-slate-600 italic">
                  வகால பிஃர்அவ்னு உஃதூனீ பிகுல்லி ஸாஹிரின் அலீம். ஃபலம்மா ஜாஅஸ் ஸஹரது கால லஹும் மூஸா அல்கூ மா அன்தும் முல்கூன். ஃபலம்மா அல்கவ் கால மூஸா மா ஜிஃதும் பிஹிஸ்ஸிஹ்ரு இன்னல்லாஹ ஸயுப்திலுஹூ இன்னல்லாஹ லா யுஸ்லிஹு அமலல் முப்ஸிதீன், வயுஹிக்குல்லாஹுல் ஹக்க பிகலிமாதிஹீ வலவ் கரிஹல் முஜ்ரிமூன்.
                </p>
                <p className="text-slate-800">
                  {isTa
                    ? "பொருள்: 'நீங்கள் கொண்டு வந்தது சூனியமே! நிச்சயமாக அல்லாஹ் அதை அழித்துவிடுவான். நிச்சயமாக அல்லாஹ் குழப்பம் விளைவிப்போரின் செயலைச் சீர்செய்ய மாட்டான்' என்று மூஸா கூறினார். குற்றவாளிகள் வெறுத்த போதும் அல்லாஹ் தன் வார்த்தைகளைக் கொண்டு சத்தியத்தை நிலை நாட்டியே தீருவான்."
                    : "Meaning: Moses said: 'What you have brought is sorcery. Indeed, Allah will make it void. Indeed, Allah does not amend the work of corrupters. And Allah will establish the truth by His words, even if the criminals hate it.'"}
                </p>
              </div>

              {/* Surah Ta-Ha 20:65-69 */}
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-extrabold text-emerald-900">3. ஸூறா தாஹா (20: 65-69)</span>
                  <button
                    type="button"
                    onClick={() =>
                      handleCopy(
                        "taha",
                        "قَالُوا يَا مُوسَىٰ إِمَّا أَن تُلْقِيَ وَإِمَّا أَن نَّكُونَ أَوَّلَ مَنْ أَلْقَىٰ ۝ قَالَ بَلْ أَلْقُوا ۖ فَإِذَا حِبَالُهُمْ وَعِصِيُّهُمْ يُخَيَّلُ إِلَيْهِ مِن سِحْرِهِمْ أَنَّهَا تَسْعَىٰ ۝ فَأَوْجَسَ فِي نَفْسِهِ خِيفَةً مُّوسَىٰ ۝ قُلْنَا لَا تَخَفْ إِنَّكَ أَنتَ الْأَعْلَىٰ ۝ وَأَلْقِ مَا فِي يَمِينِكَ تَلْقَفْ مَا صَنَعُوا ۖ إِنَّمَا صَنَعُوا كَيْدُ سَاحِرٍ ۖ وَلَا يُفْلِحُ السَّاحِرُ حَيْثُ أَتَىٰ"
                      )
                    }
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 hover:text-emerald-900"
                  >
                    {copiedKey === "taha" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedKey === "taha" ? (isTa ? "நகலெடுக்கப்பட்டது" : "Copied") : isTa ? "நகல்" : "Copy"}</span>
                  </button>
                </div>
                <p className="font-arabic text-base text-right leading-loose text-slate-900" dir="rtl">
                  قَالُوا يَا مُوسَىٰ إِمَّا أَن تُلْقِيَ وَإِمَّا أَن نَّكُونَ أَوَّلَ مَنْ أَلْقَىٰ ۝ قَالَ بَلْ أَلْقُوا ۖ فَإِذَا حِبَالُهُمْ وَعِصِيُّهُمْ يُخَيَّلُ إِلَيْهِ مِن سِحْرِهِمْ أَنَّهَا تَسْعَىٰ ۝ فَأَوْجَسَ فِي نَفْسِهِ خِيفَةً مُّوسَىٰ ۝ قُلْنَا لَا تَخَفْ إِنَّكَ أَنتَ الْأَعْلَىٰ ۝ وَأَلْقِ مَا فِي يَمِينِكَ تَلْقَفْ مَا صَنَعُوا ۖ إِنَّمَا صَنَعُوا كَيْدُ سَاحِرٍ ۖ وَلَا يُفْلِحُ السَّاحِرُ حَيْثُ أَتَىٰ ۝
                </p>
                <p className="text-slate-600 italic">
                  அச்சம் கொள்ளாதீர். நிச்சயமாக நீர்தான் மேலோங்கி நிற்பீர் என நாம் கூறினோம். உமது வலது கையில் இருப்பதை நீர் போடும். அவர்கள் செய்தவற்றை அது விழுங்கி விடும். அவர்கள் செய்தது சூனியக்காரனின் சூழ்ச்சியேயாகும். சூனியக்காரன் எங்கிருந்து வந்தாலும் வெற்றிபெற மாட்டான்.
                </p>
                <p className="text-slate-800">
                  {isTa
                    ? "பொருள்: 'அச்சம் கொள்ளாதீர்! நிச்சயமாக நீரே மேலோங்குவீர். உமது வலது கையில் உள்ள கைத்தடியைப் போடுவீராக; அவர்கள் செய்த வித்தைகளை அது விழுங்கிவிடும். நிச்சயமாக அவர்கள் செய்தது சூனியக்காரனின் சூழ்ச்சியே. சூனியக்காரன் எங்கு சென்றாலும் வெற்றி பெற மாட்டான்' (ஸூறா தாஹா 20:68-69)."
                    : "Meaning: We said: 'Fear not! Indeed, you are superior. Throw what is in your right hand; it will swallow up what they have crafted. What they crafted is merely the trick of a magician, and the magician will not succeed wherever he goes.'"}
                </p>
              </div>
            </div>
          )}

          {/* TAB 4: Daily Protection Fortress */}
          {activeTab === "daily_armor" && (
            <div className="space-y-4 text-xs">
              <div className="p-3.5 rounded-xl bg-teal-50 border border-teal-200 text-teal-950">
                <p className="font-semibold">
                  {isTa
                    ? "சூனியம் மற்றும் தீய சக்திகள் அணுகாதிருக்க நபிகள் நாயகம் (ஸல்) கற்றுத்தந்த தினசரி தற்காப்பு அரண்:"
                    : "Authentic Prophetic Fortress for immunity against devils, black magic, and envious eyes:"}
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5">
                  <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-[11px]">
                    <Moon className="w-3.5 h-3.5" />
                    <span>{isTa ? "1. ஆயதுல் குர்ஸி (பகரா 255)" : "1. Ayatul Kursi (2:255)"}</span>
                  </div>
                  <p className="text-slate-700">
                    {isTa
                      ? "ஒவ்வொரு கடமையான தொழுகைக்குப் பின்னும், தூங்கும் போதும் ஓதி வரவும். விடியும் வரை வானவர் பாதுகாப்பார்; ஷைத்தான் நெருங்க முடியாது."
                      : "Recite after each 5 fard prayers and before sleeping. A guardian angel will protect you until morning; Satan cannot come near."}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5">
                  <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-[11px]">
                    <Sun className="w-3.5 h-3.5" />
                    <span>{isTa ? "2. முஅவ்விததைன் (3 குல் ஸூராக்கள்)" : "2. The Three Quls (3 Times)"}</span>
                  </div>
                  <p className="text-slate-700">
                    {isTa
                      ? "ஃபஜ்ர் மற்றும் மஃக்ரிப் தொழுகைக்குப் பிறகு குல்ஹுவல்லாஹு அஹத், குல்அவூது பிரப்பில் பலக், குல்அவூது பிரப்பிந்நாஸ் தலா 3 முறை ஓதவும். இது அனைத்து தீங்குகளிலிருந்தும் பாதுகாக்கும்."
                      : "Recite Surah Al-Ikhlas, Surah Al-Falaq, and Surah An-Nas 3 times after Fajr and Maghrib as an impenetrable shield against all evils."}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5">
                  <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-[11px]">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{isTa ? "3. ஸூறா பகராவின் கடைசி 2 வசனங்கள்" : "3. Last 2 Verses of Al-Baqarah"}</span>
                  </div>
                  <p className="text-slate-700">
                    {isTa
                      ? "இரவில் 'ஆமனர் ரஸூலு...' வசனங்களை ஓதுதல். நபிமொழி: 'யார் ஓரிரவில் இதனை ஓதுகிறாரோ அதுவே அவரது பாதுகாப்பிற்குப் போதுமாகும்'."
                      : "Recite 'Aamanar-Rasoolu...' (2:285-286) every night. The Prophet (pbuh) said: 'Whoever recites them at night, they will suffice him.'"}
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-1.5">
                  <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-[11px]">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{isTa ? "4. பிஸ்மில்லாஹில்லதீ லா யளுர்ரு..." : "4. Bismillaahil-ladhee..."}</span>
                  </div>
                  <p className="font-arabic text-xs text-right text-emerald-950 font-semibold" dir="rtl">
                    «بِسْمِ اللَّهِ الَّذِي لَا يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ»
                  </p>
                  <p className="text-slate-700">
                    {isTa
                      ? "காலையிலும் மாலையிலும் 3 முறை ஓதி வர வானிலும் பூமியிலும் உள்ள எப்பொருளும் எவ்விதத் தீங்கும் செய்ய முடியாது."
                      : "Recite 3 times morning and evening: Nothing in heaven or earth can harm the one who invokes Allah's name."}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: Disenchantment & Marital Discord */}
          {activeTab === "disenchantment" && (
            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-2xs space-y-3">
                <div className="flex items-center gap-2 font-extrabold text-emerald-950 text-sm">
                  <HeartHandshake className="w-4 h-4 text-emerald-600" />
                  <span>
                    {isTa
                      ? "கணவன்-மனைவி தாம்பத்திய பிரிவினை சூனிய முறிவு (அஷ்ஷெய்க் பின் பாஸ் பத்வா)"
                      : "Healing Spells of Marital Discord & Separation (Sheikh Ibn Baz Fatwa)"}
                  </span>
                </div>
                <p className="text-slate-700 leading-relaxed">
                  {isTa
                    ? "கணவனுக்கும் மனைவிக்குமிடையில் எதைக்கொண்டு பிரிப்பார்களோ, அதை அவ்விருவரிடமிருந்து கற்றுக்கொண்டார்கள்; மேலும் அல்லாஹ்வின் அனுமதியின்றி அதைக்கொண்டு அவர்கள் ஒருவருக்குமே தீங்கிழைக்கக் கூடியவர்களாக இல்லை (ஸூறா அல்-பகரா 2:102). தாம்பத்திய உறவில் காரணமின்றி ஏற்படும் வெறுப்பு, தூரமாதல் அல்லது இயலாமைக்கு 7 பச்சை இலந்தை இலை நீரில் சூனிய முறிவு வசனங்களை ஓதி கணவனும் மனைவியும் பருகி குளிப்பது மிகச்சிறந்த பரிகாரமாகும்."
                    : "Witchcraft causing separation between husband and wife is explicitly referenced in Surah Al-Baqarah (2:102). Drinking and bathing with Sidr-infused Ruqyah water dissolves separation spells and restores mutual affection and marital harmony."}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 shadow-2xs space-y-3">
                <div className="flex items-center gap-2 font-extrabold text-amber-950 text-sm">
                  <Flame className="w-4 h-4 text-amber-600" />
                  <span>
                    {isTa
                      ? "செய்வினை முடிச்சுகளைக் கண்டறிந்து முறித்தல் (Physical Nullification)"
                      : "Locating and Dissolving Physical Talismans & Knotted Cords"}
                  </span>
                </div>
                <p className="text-slate-700 leading-relaxed">
                  {isTa
                    ? "சூனியத்திற்கான மிக உறுதியான நிவாரணம் என்னவெனில், சூனியம் வைக்கப்பட்ட இடத்தை கண்டறிய முயற்சித்தல். அவ்வாறு கண்டெடுக்கப்படும் முடிச்சிடப்பட்ட நூல்கள், ஆணிகள், தாயத்துக்கள், தகடுகள் ஆகியவற்றை வெளியே எடுத்து அல்-முஅவ்விததைன் (ஸூறா பலக், நாஸ்) ஓதியவாறு முடிச்சுகளை ஒவ்வொன்றாக அவிழ்த்து எரித்தோ அழித்தோ விட்டால் சூனியம் முற்றாக முறிந்துவிடும்."
                    : "The most definitive cure is discovering where the talisman was buried or hidden. Untying all knots while reciting Surah Al-Falaq and Surah An-Nas, and subsequently burning or disposing of the articles completely shatters the witchcraft."}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
