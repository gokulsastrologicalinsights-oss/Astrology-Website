"use client";

import React, { useState, useEffect, useRef, useMemo } from "react";
import { Search, X, Loader2, Sparkles, User, Calendar, MapPin, Hash } from "lucide-react";
import { formatDate } from "@/lib/date-formatter";

export interface SearchSuggestionItem {
  id: string | number;
  title: string; // The primary name/title (e.g. "Gokul", "Gokul Krishnan")
  subtitle?: string; // e.g. "DOB: 15/05/1998 • Chennai"
  badge?: string; // e.g. "#01" or "Natal" or "Horary"
  category?: string; // Optional group name
  data?: any; // The original item payload
}

export interface SavedChatSearchProps<T = any> {
  // Mode 1: Static items in memory (client-side matching)
  items?: T[];
  // Converter from item T to SearchSuggestionItem
  getItemSuggestion?: (item: T) => SearchSuggestionItem;

  // Mode 2: Async server-side fetcher
  onSearchAsync?: (query: string) => Promise<SearchSuggestionItem[]>;

  // Callbacks
  onSelect: (item: SearchSuggestionItem) => void;
  onSearchSubmit?: (query: string) => void;
  onClear?: () => void;

  // Customization
  placeholder?: string;
  buttonText?: string;
  className?: string;
  inputClassName?: string;
  themeColor?: string; // e.g. "#153F6B" or "#B8860B"
  minQueryLength?: number; // default 1
  maxSuggestions?: number; // default 8
  language?: "en" | "ta";
  initialValue?: string;
  autoFocus?: boolean;
}

export function SavedChatSearch<T = any>({
  items,
  getItemSuggestion,
  onSearchAsync,
  onSelect,
  onSearchSubmit,
  onClear,
  placeholder,
  buttonText,
  className = "",
  inputClassName = "",
  themeColor = "#153F6B",
  minQueryLength = 1,
  maxSuggestions = 8,
  language = "ta",
  initialValue = "",
  autoFocus = false,
}: SavedChatSearchProps<T>) {
  const [query, setQuery] = useState(initialValue);
  const [isOpen, setIsOpen] = useState(false);
  const [asyncResults, setAsyncResults] = useState<SearchSuggestionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sync initialValue if changed
  useEffect(() => {
    if (initialValue !== undefined) {
      setQuery(initialValue);
    }
  }, [initialValue]);

  // Click outside listener to close suggestion dropdown
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Compute suggestions from memory items
  const localSuggestions = useMemo<SearchSuggestionItem[]>(() => {
    if (!items || !items.length || onSearchAsync) return [];
    const q = query.trim().toLowerCase();
    if (q.length < minQueryLength) return [];

    const mapped: SearchSuggestionItem[] = items.map((it, idx) => {
      if (getItemSuggestion) return getItemSuggestion(it);

      // Default duck-typing for standard records
      const raw = it as any;
      const title =
        raw.person_name ||
        raw.title ||
        raw.name ||
        raw.groom_name ||
        `Record #${raw.display_number || idx + 1}`;
      
      const dob = raw.birth_date ? formatDate(raw.birth_date) : "";
      const place = raw.birthplace || raw.location_name || "";
      const subParts = [dob ? `DOB: ${dob}` : "", place].filter(Boolean);

      return {
        id: raw.id || idx,
        title,
        subtitle: subParts.join(" • "),
        badge: raw.display_number ? `#${raw.display_number}` : undefined,
        data: raw,
      };
    });

    // Filter items matching query in title or subtitle
    return mapped
      .filter((s) => {
        const titleMatch = s.title.toLowerCase().includes(q);
        const subMatch = s.subtitle ? s.subtitle.toLowerCase().includes(q) : false;
        const badgeMatch = s.badge ? s.badge.toLowerCase().includes(q) : false;
        return titleMatch || subMatch || badgeMatch;
      })
      .slice(0, maxSuggestions);
  }, [items, getItemSuggestion, onSearchAsync, query, minQueryLength, maxSuggestions]);

  // Trigger async search when typing if onSearchAsync is provided
  useEffect(() => {
    if (!onSearchAsync) return;
    const q = query.trim();
    if (q.length < minQueryLength) {
      setAsyncResults([]);
      setIsLoading(false);
      return;
    }

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    setIsLoading(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const results = await onSearchAsync(q);
        setAsyncResults(results.slice(0, maxSuggestions));
      } catch (err) {
        console.error("Async search error:", err);
        setAsyncResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 250);

    return () => {
      if (debounceTimerRef.current) clearTimeout(debounceTimerRef.current);
    };
  }, [query, onSearchAsync, minQueryLength, maxSuggestions]);

  // Active suggestions list
  const activeSuggestions = onSearchAsync ? asyncResults : localSuggestions;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    setIsOpen(true);
    setHighlightedIndex(-1);
  };

  const handleClear = () => {
    setQuery("");
    setIsOpen(false);
    setHighlightedIndex(-1);
    setAsyncResults([]);
    onClear?.();
    inputRef.current?.focus();
  };

  const handleSelectSuggestion = (suggestion: SearchSuggestionItem) => {
    setQuery(suggestion.title);
    setIsOpen(false);
    setHighlightedIndex(-1);
    onSelect(suggestion);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!isOpen && activeSuggestions.length > 0) {
        setIsOpen(true);
      }
      setHighlightedIndex((prev) =>
        prev < activeSuggestions.length - 1 ? prev + 1 : 0
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) =>
        prev > 0 ? prev - 1 : activeSuggestions.length - 1
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (isOpen && highlightedIndex >= 0 && activeSuggestions[highlightedIndex]) {
        handleSelectSuggestion(activeSuggestions[highlightedIndex]);
      } else {
        setIsOpen(false);
        onSearchSubmit?.(query.trim());
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
      setHighlightedIndex(-1);
    }
  };

  const defaultPlaceholder = language === "ta" ? "தேடுக... (எ.கா: Gokul)" : "Search... (e.g. Gokul)";
  const defaultButtonText = language === "ta" ? "கண்டுபிடி" : "Search";

  // Helper to highlight matching text in title
  const renderHighlightedText = (text: string, highlight: string) => {
    if (!highlight.trim()) return text;
    const parts = text.split(new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === highlight.toLowerCase() ? (
            <mark key={i} className="bg-amber-100 text-amber-950 font-bold rounded-xs px-0.5">
              {part}
            </mark>
          ) : (
            part
          )
        )}
      </span>
    );
  };

  return (
    <div ref={containerRef} className={`relative flex items-center gap-2 ${className}`}>
      {/* Input Box with live dropdown */}
      <div className="relative flex-1">
        <input
          ref={inputRef}
          type="text"
          value={query}
          autoFocus={autoFocus}
          onChange={handleInputChange}
          onFocus={() => {
            if (query.trim().length >= minQueryLength) setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || defaultPlaceholder}
          className={`w-full px-3 py-1.5 text-xs text-[#183047] placeholder-[#8190A6] border border-[#D9DEE7] rounded-lg focus:outline-hidden focus:border-[#153F6B] focus:ring-1 focus:ring-[#153F6B]/20 transition-all bg-white pr-7 ${inputClassName}`}
        />

        {isLoading ? (
          <Loader2 className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#153F6B] animate-spin pointer-events-none" />
        ) : query ? (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-0.5 rounded text-[#8190A6] hover:text-[#183047] cursor-pointer"
            title="Clear"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        ) : null}

        {/* Live Suggestions Dropdown directly beneath input */}
        {isOpen && query.trim().length >= minQueryLength && (
          <div className="absolute left-0 right-0 top-full mt-1.5 z-50 bg-white rounded-xl border border-[#D9DEE7] shadow-xl overflow-hidden max-h-72 overflow-y-auto animate-in fade-in zoom-in-95 duration-100">
            {activeSuggestions.length > 0 ? (
              <div className="py-1">
                <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-[#8190A6] bg-[#FAF8F5] border-b border-[#F0ECE1]">
                  {language === "ta" ? "பொருத்தமான பரிந்துரைகள்" : "Matching Suggestions"}
                </div>
                {activeSuggestions.map((item, idx) => {
                  const isHighlighted = idx === highlightedIndex;
                  return (
                    <button
                      key={`${item.id}-${idx}`}
                      type="button"
                      onClick={() => handleSelectSuggestion(item)}
                      onMouseEnter={() => setHighlightedIndex(idx)}
                      className={`w-full text-left px-3 py-2 flex items-center justify-between gap-3 text-xs transition-colors cursor-pointer ${
                        isHighlighted
                          ? "bg-[#FAF2DE] text-[#153F6B]"
                          : "hover:bg-[#FAF8F5] text-[#183047]"
                      }`}
                    >
                      <div className="min-w-0 flex-1">
                        <div className="font-semibold truncate flex items-center gap-1.5">
                          <User className="w-3 h-3 text-[#B8860B] shrink-0" />
                          <span>{renderHighlightedText(item.title, query)}</span>
                        </div>
                        {item.subtitle && (
                          <div className="text-[11px] text-[#8190A6] truncate mt-0.5 pl-4.5">
                            {item.subtitle}
                          </div>
                        )}
                      </div>

                      {item.badge && (
                        <span className="shrink-0 font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ) : !isLoading ? (
              <div className="p-4 text-center text-xs text-[#8190A6]">
                {language === "ta"
                  ? `"${query}" என்ற பெயரில் பதிவுகள் எதுவும் காணப்படவில்லை.`
                  : `No saved records matching "${query}".`}
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Primary Search Button */}
      <button
        type="button"
        onClick={() => {
          setIsOpen(false);
          onSearchSubmit?.(query.trim());
        }}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-white text-xs font-semibold shadow-2xs transition-colors cursor-pointer shrink-0"
        style={{ backgroundColor: themeColor }}
      >
        <Search className="w-3.5 h-3.5" />
        <span>{buttonText || defaultButtonText}</span>
      </button>
    </div>
  );
}
