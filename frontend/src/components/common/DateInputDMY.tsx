"use client";

import React, { useState, useEffect, useRef, useId, useCallback } from "react";
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, X } from "lucide-react";
import { parseDateInput } from "@/lib/date-formatter";

export interface DateInputDMYProps {
  id?: string;
  name?: string;
  value?: string | null;
  onChange?: (e: any) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  containerClassName?: string;
  required?: boolean;
  disabled?: boolean;
  autoComplete?: string;
  minDate?: string; // YYYY-MM-DD
  maxDate?: string; // YYYY-MM-DD
  error?: boolean | string;
  language?: "en" | "ta";
  title?: string;
  style?: React.CSSProperties;
  "data-lpignore"?: string;
  "data-form-type"?: string;
  [key: string]: any;
}

const MONTH_NAMES_EN = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const MONTH_NAMES_TA = [
  "ஜனவரி", "பிப்ரவரி", "மார்ச்", "ஏப்ரல்", "மே", "ஜூன்",
  "ஜூலை", "ஆகஸ்ட்", "செப்டம்பர்", "அக்டோபர்", "நவம்பர்", "டிசம்பர்"
];

const WEEKDAY_NAMES_EN = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
const WEEKDAY_NAMES_TA = ["ஞா", "தி", "செ", "பு", "வி", "வெ", "ச"];

/**
 * Converts a raw ISO (YYYY-MM-DD) or other valid date input into DD/MM/YYYY display string
 */
function toDisplayDMY(raw: string | null | undefined): string {
  if (!raw) return "";
  const parts = parseDateInput(raw);
  if (!parts) return "";
  const dd = String(parts.day).padStart(2, "0");
  const mm = String(parts.month).padStart(2, "0");
  const yyyy = String(parts.year).padStart(4, "0");
  return `${dd}/${mm}/${yyyy}`;
}

/**
 * Converts DD/MM/YYYY string to ISO YYYY-MM-DD if valid, else returns empty string
 */
function dmyToIso(dmy: string): string {
  const match = dmy.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!match) return "";
  const day = parseInt(match[1], 10);
  const month = parseInt(match[2], 10);
  const year = parseInt(match[3], 10);

  if (year < 1800 || year > 2200 || month < 1 || month > 12) return "";
  const daysInMonth = new Date(year, month, 0).getDate();
  if (day < 1 || day > daysInMonth) return "";

  const yyyy = String(year).padStart(4, "0");
  const mm = String(month).padStart(2, "0");
  const dd = String(day).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export function DateInputDMY({
  id,
  name,
  value,
  onChange,
  onBlur,
  placeholder = "DD/MM/YYYY",
  className = "",
  containerClassName = "",
  required = false,
  disabled = false,
  autoComplete = "off",
  minDate,
  maxDate,
  error,
  language = "en",
  title,
  style,
  "data-lpignore": lpignore,
  "data-form-type": formType,
  ...restProps
}: DateInputDMYProps) {
  const generatedId = useId();
  const inputId = id || generatedId;

  // Display text in input box: strictly DD/MM/YYYY
  const [displayText, setDisplayText] = useState(() => toDisplayDMY(value));
  const [isOpen, setIsOpen] = useState(false);

  // Calendar navigation state
  const today = new Date();
  const [viewYear, setViewYear] = useState(() => {
    const parts = parseDateInput(value);
    return parts ? parts.year : today.getFullYear();
  });
  const [viewMonth, setViewMonth] = useState(() => {
    const parts = parseDateInput(value);
    return parts ? parts.month - 1 : today.getMonth(); // 0-based
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Synchronize internal display when value prop changes externally
  useEffect(() => {
    const formatted = toDisplayDMY(value);
    setDisplayText(formatted);
    if (value) {
      const parts = parseDateInput(value);
      if (parts) {
        setViewYear(parts.year);
        setViewMonth(parts.month - 1);
      }
    }
  }, [value]);

  // Dispatch change event to parent with ISO YYYY-MM-DD
  const triggerChange = useCallback(
    (isoValue: string) => {
      if (!onChange) return;
      const syntheticEvent = {
        target: {
          value: isoValue,
          name: name || inputId,
          id: inputId,
        },
        currentTarget: {
          value: isoValue,
          name: name || inputId,
          id: inputId,
        },
        preventDefault: () => {},
        stopPropagation: () => {},
      };
      // Support both event-style onChange(e) and direct string onChange(val)
      try {
        onChange(syntheticEvent);
      } catch {
        onChange(isoValue as any);
      }
    },
    [onChange, name, inputId]
  );

  // Masked typing logic for DD/MM/YYYY
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawVal = e.target.value;
    // Extract only digits
    const digits = rawVal.replace(/\D/g, "").slice(0, 8);

    let formatted = "";
    if (digits.length > 0) {
      formatted = digits.slice(0, 2);
      if (digits.length >= 2) {
        formatted += "/" + digits.slice(2, 4);
      }
      if (digits.length >= 4) {
        formatted += "/" + digits.slice(4, 8);
      }
    }

    setDisplayText(formatted);

    if (formatted.length === 10) {
      const iso = dmyToIso(formatted);
      if (iso) {
        triggerChange(iso);
        const parts = parseDateInput(iso);
        if (parts) {
          setViewYear(parts.year);
          setViewMonth(parts.month - 1);
        }
      } else {
        triggerChange("");
      }
    } else if (formatted.length === 0) {
      triggerChange("");
    }
  };

  // Close calendar popover on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Handle day selection in calendar popover
  const handleSelectDay = (day: number) => {
    const yyyy = String(viewYear).padStart(4, "0");
    const mm = String(viewMonth + 1).padStart(2, "0");
    const dd = String(day).padStart(2, "0");
    const iso = `${yyyy}-${mm}-${dd}`;
    const dmy = `${dd}/${mm}/${yyyy}`;

    setDisplayText(dmy);
    triggerChange(iso);
    setIsOpen(false);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  // Month navigation
  const prevMonth = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear((y) => y - 1);
    } else {
      setViewMonth((m) => m - 1);
    }
  };

  const nextMonth = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear((y) => y + 1);
    } else {
      setViewMonth((m) => m + 1);
    }
  };

  // Calendar computation
  const daysInViewMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const firstDayOfWeek = new Date(viewYear, viewMonth, 1).getDay(); // 0 is Sunday

  const currentParts = parseDateInput(value || (displayText.length === 10 ? dmyToIso(displayText) : null));
  const selectedDay =
    currentParts && currentParts.year === viewYear && currentParts.month === viewMonth + 1
      ? currentParts.day
      : null;

  // Year choices range: 1900 to 2050
  const yearOptions: number[] = [];
  const currentYear = today.getFullYear();
  for (let y = currentYear + 10; y >= 1920; y--) {
    yearOptions.push(y);
  }

  const monthNames = language === "ta" ? MONTH_NAMES_TA : MONTH_NAMES_EN;
  const weekdayNames = language === "ta" ? WEEKDAY_NAMES_TA : WEEKDAY_NAMES_EN;

  return (
    <div ref={containerRef} className={`relative inline-block w-full ${containerClassName}`}>
      {/* Hidden input storing the ISO value for standard form submissions */}
      <input type="hidden" name={name} value={dmyToIso(displayText) || ""} />

      {/* Visible Input Box strictly enforcing DD/MM/YYYY */}
      <div className="relative flex items-center">
        <input
          ref={inputRef}
          id={inputId}
          type="text"
          inputMode="numeric"
          autoComplete={autoComplete}
          required={required}
          disabled={disabled}
          placeholder={placeholder}
          value={displayText}
          onChange={handleInputChange}
          onBlur={onBlur}
          title={title}
          style={style}
          maxLength={10}
          data-lpignore={lpignore}
          data-form-type={formType}
          {...restProps}
          className={`${className} pr-10 tracking-wide font-medium`}
        />

        {/* Calendar Picker Trigger Icon */}
        <button
          type="button"
          disabled={disabled}
          onClick={() => setIsOpen((prev) => !prev)}
          className="absolute right-2.5 p-1 text-slate-400 hover:text-[#B8860B] transition-colors cursor-pointer rounded-md focus:outline-hidden disabled:opacity-50 disabled:cursor-not-allowed"
          title={language === "ta" ? "தேதியை தேர்ந்தெடுக்கவும் (DD/MM/YYYY)" : "Select Date (DD/MM/YYYY)"}
          tabIndex={-1}
        >
          <CalendarIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Floating Interactive Calendar Popover */}
      {isOpen && (
        <div
          className="absolute left-0 top-full mt-1.5 z-50 w-72 rounded-xl border border-slate-200 bg-white p-3.5 shadow-xl text-slate-800 animate-in fade-in zoom-in-95 duration-100"
          style={{ minWidth: "280px" }}
        >
          {/* Header: Month & Year Nav */}
          <div className="flex items-center justify-between gap-1.5 mb-3">
            <button
              type="button"
              onClick={prevMonth}
              className="p-1 rounded-lg hover:bg-slate-100 text-slate-600 transition cursor-pointer"
              title="Previous Month"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-1.5">
              {/* Month Dropdown */}
              <select
                value={viewMonth}
                onChange={(e) => setViewMonth(parseInt(e.target.value, 10))}
                className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-slate-800 focus:outline-hidden focus:border-[#B8860B]"
              >
                {monthNames.map((name, idx) => (
                  <option key={idx} value={idx}>
                    {name}
                  </option>
                ))}
              </select>

              {/* Year Dropdown */}
              <select
                value={viewYear}
                onChange={(e) => setViewYear(parseInt(e.target.value, 10))}
                className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-slate-800 focus:outline-hidden focus:border-[#B8860B]"
              >
                {yearOptions.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={nextMonth}
              className="p-1 rounded-lg hover:bg-slate-100 text-slate-600 transition cursor-pointer"
              title="Next Month"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          {/* Weekday Header */}
          <div className="grid grid-cols-7 gap-1 text-center mb-1 text-[11px] font-semibold text-slate-400">
            {weekdayNames.map((w, i) => (
              <div key={i} className="py-0.5">
                {w}
              </div>
            ))}
          </div>

          {/* Days Grid */}
          <div className="grid grid-cols-7 gap-1 text-center text-xs">
            {/* Empty padding before day 1 */}
            {Array.from({ length: firstDayOfWeek }).map((_, i) => (
              <div key={`empty-${i}`} className="p-1.5" />
            ))}

            {/* Days in current month */}
            {Array.from({ length: daysInViewMonth }).map((_, i) => {
              const dayNum = i + 1;
              const isSelected = selectedDay === dayNum;
              const isToday =
                today.getFullYear() === viewYear &&
                today.getMonth() === viewMonth &&
                today.getDate() === dayNum;

              return (
                <button
                  key={dayNum}
                  type="button"
                  onClick={() => handleSelectDay(dayNum)}
                  className={`py-1.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                    isSelected
                      ? "bg-[#B8860B] text-white font-bold shadow-xs"
                      : isToday
                      ? "bg-amber-100 text-amber-900 font-bold hover:bg-amber-200"
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {dayNum}
                </button>
              );
            })}
          </div>

          {/* Footer Quick Actions */}
          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
            <button
              type="button"
              onClick={() => {
                const now = new Date();
                setViewYear(now.getFullYear());
                setViewMonth(now.getMonth());
                handleSelectDay(now.getDate());
              }}
              className="text-[#B8860B] hover:underline font-semibold cursor-pointer"
            >
              {language === "ta" ? "இன்று" : "Today"}
            </button>
            <button
              type="button"
              onClick={() => {
                setDisplayText("");
                triggerChange("");
                setIsOpen(false);
              }}
              className="text-slate-400 hover:text-red-600 transition cursor-pointer"
            >
              {language === "ta" ? "அழிக்க" : "Clear"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
