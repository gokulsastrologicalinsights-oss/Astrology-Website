"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useLanguage } from "@/lib/i18n";
import { Clock, Sun, Moon } from "lucide-react";

interface YamamSlot {
  time: string;
  nameTa: string;
  nameEn: string;
  power: string;
  color: string;
  startMin: number;
  endMin: number;
}

interface DayData {
  dayIndex: number;
  nameTa: string;
  nameEn: string;
  rahu: string;
  rahuMin: [number, number];
  yama: string;
  yamaMin: [number, number];
  nalla: string;
  kuligai: string;
  dayYamams: YamamSlot[];
  nightYamams: YamamSlot[];
}

const YAMAM_TIMES = [
  { time: "06:00 - 08:24 AM", startMin: 360, endMin: 504 },
  { time: "08:24 - 10:48 AM", startMin: 504, endMin: 648 },
  { time: "10:48 - 01:12 PM", startMin: 648, endMin: 792 },
  { time: "01:12 - 03:36 PM", startMin: 792, endMin: 936 },
  { time: "03:36 - 06:00 PM", startMin: 936, endMin: 1080 },
];

const NIGHT_TIMES = [
  { time: "06:00 - 08:24 PM", startMin: 1080, endMin: 1224 },
  { time: "08:24 - 10:48 PM", startMin: 1224, endMin: 1368 },
  { time: "10:48 - 01:12 AM", startMin: 1368, endMin: 1512 },
  { time: "01:12 - 03:36 AM", startMin: 72, endMin: 216 },
  { time: "03:36 - 06:00 AM", startMin: 216, endMin: 360 },
];

const ACT = {
  arasu: { nameTa: "அரசு", nameEn: "Ruling", power: "100%", color: "bg-emerald-600 text-white" },
  oon: { nameTa: "ஊண்", nameEn: "Eating", power: "80%", color: "bg-sky-600 text-white" },
  nadai: { nameTa: "நடை", nameEn: "Walking", power: "50%", color: "bg-amber-600 text-white" },
  thuyil: { nameTa: "துயில்", nameEn: "Sleeping", power: "20%", color: "bg-purple-600 text-white" },
  saavu: { nameTa: "சாவு", nameEn: "Dying", power: "0%", color: "bg-rose-600 text-white" },
};

// Cock (கோழி) in Krishna Paksha (Punarpoosam Theipirai)
const DAYS: DayData[] = [
  // 0: Sunday
  {
    dayIndex: 0,
    nameTa: "ஞாயிறு",
    nameEn: "Sun",
    rahu: "04:30 PM - 06:00 PM",
    rahuMin: [990, 1080],
    yama: "12:00 PM - 01:30 PM",
    yamaMin: [720, 810],
    nalla: "காலை 07:30 - 08:30 | மாலை 03:30 - 04:30",
    kuligai: "03:00 PM - 04:30 PM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.arasu },
      { ...YAMAM_TIMES[1], ...ACT.oon },
      { ...YAMAM_TIMES[2], ...ACT.nadai },
      { ...YAMAM_TIMES[3], ...ACT.thuyil },
      { ...YAMAM_TIMES[4], ...ACT.saavu },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.thuyil },
      { ...NIGHT_TIMES[1], ...ACT.oon },
      { ...NIGHT_TIMES[2], ...ACT.arasu },
      { ...NIGHT_TIMES[3], ...ACT.saavu },
      { ...NIGHT_TIMES[4], ...ACT.nadai },
    ],
  },
  // 1: Monday
  {
    dayIndex: 1,
    nameTa: "திங்கள்",
    nameEn: "Mon",
    rahu: "07:30 AM - 09:00 AM",
    rahuMin: [450, 540],
    yama: "10:30 AM - 12:00 PM",
    yamaMin: [630, 720],
    nalla: "காலை 06:30 - 07:30 | மாலை 04:30 - 05:30",
    kuligai: "01:30 PM - 03:00 PM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.thuyil },
      { ...YAMAM_TIMES[1], ...ACT.saavu },
      { ...YAMAM_TIMES[2], ...ACT.arasu },
      { ...YAMAM_TIMES[3], ...ACT.oon },
      { ...YAMAM_TIMES[4], ...ACT.nadai },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.oon },
      { ...NIGHT_TIMES[1], ...ACT.arasu },
      { ...NIGHT_TIMES[2], ...ACT.saavu },
      { ...NIGHT_TIMES[3], ...ACT.nadai },
      { ...NIGHT_TIMES[4], ...ACT.thuyil },
    ],
  },
  // 2: Tuesday
  {
    dayIndex: 2,
    nameTa: "செவ்வாய்",
    nameEn: "Tue",
    rahu: "03:00 PM - 04:30 PM",
    rahuMin: [900, 990],
    yama: "09:00 AM - 10:30 AM",
    yamaMin: [540, 630],
    nalla: "காலை 07:30 - 08:30 | மாலை 04:30 - 05:30",
    kuligai: "12:00 PM - 01:30 PM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.arasu },
      { ...YAMAM_TIMES[1], ...ACT.oon },
      { ...YAMAM_TIMES[2], ...ACT.nadai },
      { ...YAMAM_TIMES[3], ...ACT.thuyil },
      { ...YAMAM_TIMES[4], ...ACT.saavu },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.thuyil },
      { ...NIGHT_TIMES[1], ...ACT.oon },
      { ...NIGHT_TIMES[2], ...ACT.arasu },
      { ...NIGHT_TIMES[3], ...ACT.saavu },
      { ...NIGHT_TIMES[4], ...ACT.nadai },
    ],
  },
  // 3: Wednesday
  {
    dayIndex: 3,
    nameTa: "புதன்",
    nameEn: "Wed",
    rahu: "12:00 PM - 01:30 PM",
    rahuMin: [720, 810],
    yama: "07:30 AM - 09:00 AM",
    yamaMin: [450, 540],
    nalla: "காலை 09:30 - 10:30 | மாலை 04:30 - 05:30",
    kuligai: "10:30 AM - 12:00 PM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.nadai },
      { ...YAMAM_TIMES[1], ...ACT.thuyil },
      { ...YAMAM_TIMES[2], ...ACT.saavu },
      { ...YAMAM_TIMES[3], ...ACT.arasu },
      { ...YAMAM_TIMES[4], ...ACT.oon },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.arasu },
      { ...NIGHT_TIMES[1], ...ACT.saavu },
      { ...NIGHT_TIMES[2], ...ACT.nadai },
      { ...NIGHT_TIMES[3], ...ACT.thuyil },
      { ...NIGHT_TIMES[4], ...ACT.oon },
    ],
  },
  // 4: Thursday
  {
    dayIndex: 4,
    nameTa: "வியாழன்",
    nameEn: "Thu",
    rahu: "01:30 PM - 03:00 PM",
    rahuMin: [810, 900],
    yama: "06:00 AM - 07:30 AM",
    yamaMin: [360, 450],
    nalla: "காலை 09:30 - 10:30 | மாலை 06:30 - 07:30",
    kuligai: "09:00 AM - 10:30 AM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.oon },
      { ...YAMAM_TIMES[1], ...ACT.nadai },
      { ...YAMAM_TIMES[2], ...ACT.thuyil },
      { ...YAMAM_TIMES[3], ...ACT.saavu },
      { ...YAMAM_TIMES[4], ...ACT.arasu },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.saavu },
      { ...NIGHT_TIMES[1], ...ACT.nadai },
      { ...NIGHT_TIMES[2], ...ACT.thuyil },
      { ...NIGHT_TIMES[3], ...ACT.oon },
      { ...NIGHT_TIMES[4], ...ACT.arasu },
    ],
  },
  // 5: Friday
  {
    dayIndex: 5,
    nameTa: "வெள்ளி",
    nameEn: "Fri",
    rahu: "10:30 AM - 12:00 PM",
    rahuMin: [630, 720],
    yama: "03:00 PM - 04:30 PM",
    yamaMin: [900, 990],
    nalla: "காலை 09:30 - 10:30 | மாலை 04:30 - 05:30",
    kuligai: "07:30 AM - 09:00 AM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.saavu },
      { ...YAMAM_TIMES[1], ...ACT.arasu },
      { ...YAMAM_TIMES[2], ...ACT.oon },
      { ...YAMAM_TIMES[3], ...ACT.nadai },
      { ...YAMAM_TIMES[4], ...ACT.thuyil },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.nadai },
      { ...NIGHT_TIMES[1], ...ACT.thuyil },
      { ...NIGHT_TIMES[2], ...ACT.oon },
      { ...NIGHT_TIMES[3], ...ACT.arasu },
      { ...NIGHT_TIMES[4], ...ACT.saavu },
    ],
  },
  // 6: Saturday
  {
    dayIndex: 6,
    nameTa: "சனி",
    nameEn: "Sat",
    rahu: "09:00 AM - 10:30 AM",
    rahuMin: [540, 630],
    yama: "01:30 PM - 03:00 PM",
    yamaMin: [810, 900],
    nalla: "காலை 07:30 - 08:30 | மாலை 04:30 - 05:30",
    kuligai: "06:00 AM - 07:30 AM",
    dayYamams: [
      { ...YAMAM_TIMES[0], ...ACT.arasu },
      { ...YAMAM_TIMES[1], ...ACT.oon },
      { ...YAMAM_TIMES[2], ...ACT.nadai },
      { ...YAMAM_TIMES[3], ...ACT.thuyil },
      { ...YAMAM_TIMES[4], ...ACT.saavu },
    ],
    nightYamams: [
      { ...NIGHT_TIMES[0], ...ACT.thuyil },
      { ...NIGHT_TIMES[1], ...ACT.oon },
      { ...NIGHT_TIMES[2], ...ACT.arasu },
      { ...NIGHT_TIMES[3], ...ACT.saavu },
      { ...NIGHT_TIMES[4], ...ACT.nadai },
    ],
  },
];

export function DailyTimingsWidget() {
  const { language } = useLanguage();
  const [now, setNow] = useState<Date>(new Date());
  const todayIndex = now.getDay();
  const [selectedDayIndex, setSelectedDayIndex] = useState<number>(todayIndex);
  const [isNight, setIsNight] = useState<boolean>(false);

  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const curMin = now.getHours() * 60 + now.getMinutes();
  const isSelectedToday = selectedDayIndex === todayIndex;
  const day = DAYS[selectedDayIndex] || DAYS[0];

  const activeYamamIdx = useMemo(() => {
    if (!isSelectedToday) return -1;
    const list = isNight ? day.nightYamams : day.dayYamams;
    return list.findIndex((s) => {
      if (s.startMin < s.endMin) {
        return curMin >= s.startMin && curMin < s.endMin;
      }
      return curMin >= s.startMin || curMin < (s.endMin % 1440);
    });
  }, [isSelectedToday, isNight, curMin, day]);

  return (
    <div className="w-full rounded-2xl border border-[#DDE5F0] bg-white p-4 sm:p-5 shadow-xs space-y-4">
      {/* Top Bar: Title + Day Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-3 border-b border-[#F1F5F9]">
        <div className="flex items-center gap-2">
          <span className="text-xl">🐓</span>
          <div>
            <h3 className="font-serif font-bold text-base sm:text-lg text-[#102A4C]">
              {language === "ta"
                ? "புனர்பூசம் தேய்பிறை (பட்சி: கோழி) & தினசரி நேரங்கள்"
                : "Punarvasu Krishna (Cock) & Daily Timings"}
            </h3>
            <div className="text-xs text-[#52667E] flex items-center gap-2">
              <span>{day.nameTa}க்கிழமை</span>
              <span>•</span>
              <span className="font-mono text-[11px] text-[#102A4C]">
                {now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
              </span>
            </div>
          </div>
        </div>

        {/* 7-Day Buttons */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {DAYS.map((d) => {
            const isSel = d.dayIndex === selectedDayIndex;
            const isTod = d.dayIndex === todayIndex;
            return (
              <button
                key={d.dayIndex}
                type="button"
                onClick={() => setSelectedDayIndex(d.dayIndex)}
                className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  isSel
                    ? "bg-[#102A4C] text-white shadow-xs"
                    : "bg-[#F1F5F9] text-[#52667E] hover:bg-slate-200"
                }`}
              >
                {d.nameTa}
                {isTod && (
                  <span className={`ml-1 text-[9px] px-1 rounded ${isSel ? "bg-amber-400 text-[#102A4C]" : "bg-amber-200 text-amber-900"}`}>
                    இன்று
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* 4 Timing Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Rahu */}
        <div className="p-3.5 rounded-xl border border-rose-200 bg-rose-50/40">
          <div className="text-xs font-bold text-rose-700 flex items-center justify-between">
            <span>ராகு காலம்</span>
            {isSelectedToday && curMin >= day.rahuMin[0] && curMin < day.rahuMin[1] && (
              <span className="px-1.5 py-0.2 rounded text-[9px] bg-rose-600 text-white animate-pulse">நடப்பு</span>
            )}
          </div>
          <div className="text-sm sm:text-base font-bold text-[#102A4C] mt-1">{day.rahu}</div>
        </div>

        {/* Yamagandam */}
        <div className="p-3.5 rounded-xl border border-amber-200 bg-amber-50/40">
          <div className="text-xs font-bold text-amber-800 flex items-center justify-between">
            <span>எமகண்டம்</span>
            {isSelectedToday && curMin >= day.yamaMin[0] && curMin < day.yamaMin[1] && (
              <span className="px-1.5 py-0.2 rounded text-[9px] bg-amber-600 text-white animate-pulse">நடப்பு</span>
            )}
          </div>
          <div className="text-sm sm:text-base font-bold text-[#102A4C] mt-1">{day.yama}</div>
        </div>

        {/* Nalla Neram */}
        <div className="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/40">
          <div className="text-xs font-bold text-emerald-800">நல்ல நேரம்</div>
          <div className="text-xs font-bold text-emerald-900 mt-1 leading-snug">{day.nalla}</div>
        </div>

        {/* Kuligai */}
        <div className="p-3.5 rounded-xl border border-blue-200 bg-blue-50/40">
          <div className="text-xs font-bold text-blue-800">குளிகை நேரம்</div>
          <div className="text-sm sm:text-base font-bold text-[#102A4C] mt-1">{day.kuligai}</div>
        </div>
      </div>

      {/* Panja Patchi: Punarpoosam Theipirai 5 Yamams */}
      <div className="p-3.5 rounded-xl border border-[#DDE5F0] bg-[#FAFBFD] space-y-2.5">
        <div className="flex items-center justify-between gap-2">
          <span className="text-xs font-bold text-[#102A4C]">
            புனர்பூசம் தேய்பிறை பட்சி: <strong className="text-emerald-700">கோழி 🐓</strong> (5 யாம காலங்கள்)
          </span>

          <div className="inline-flex rounded-lg p-0.5 bg-slate-200 text-[11px] font-semibold">
            <button
              type="button"
              onClick={() => setIsNight(false)}
              className={`px-2 py-0.5 rounded-md cursor-pointer flex items-center gap-1 ${
                !isNight ? "bg-white text-emerald-800 font-bold shadow-xs" : "text-slate-600"
              }`}
            >
              <Sun className="w-3 h-3 text-amber-500" />
              <span>பகல்</span>
            </button>
            <button
              type="button"
              onClick={() => setIsNight(true)}
              className={`px-2 py-0.5 rounded-md cursor-pointer flex items-center gap-1 ${
                isNight ? "bg-white text-indigo-900 font-bold shadow-xs" : "text-slate-600"
              }`}
            >
              <Moon className="w-3 h-3 text-indigo-500" />
              <span>இரவு</span>
            </button>
          </div>
        </div>

        {/* 5 Yamams Simple Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
          {(isNight ? day.nightYamams : day.dayYamams).map((slot, idx) => {
            const isLive = isSelectedToday && idx === activeYamamIdx;
            return (
              <div
                key={idx}
                className={`p-2.5 rounded-lg border text-center transition-all ${
                  isLive
                    ? "bg-white border-emerald-500 ring-2 ring-emerald-400 shadow-sm"
                    : "bg-white border-[#E2E8F0]"
                }`}
              >
                <div className="text-[10px] text-[#52667E]">{slot.time}</div>
                <div className="mt-1 flex items-center justify-center gap-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold ${slot.color}`}>
                    {slot.nameTa}
                  </span>
                  <span className="text-[10px] font-bold text-[#52667E]">{slot.power}</span>
                </div>
                {isLive && (
                  <span className="mt-1 inline-block text-[9px] font-extrabold text-emerald-700 uppercase">
                    ● நடப்பு
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
