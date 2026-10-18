"use client";

import React from "react";
import Link from "next/link";
import { ChevronRight, Home } from "lucide-react";

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumbs({ items, className = "" }: BreadcrumbsProps) {
  return (
    <nav aria-label="Breadcrumb" className={`flex items-center text-xs text-[#52667E] ${className}`}>
      <ol className="flex items-center flex-wrap gap-1.5">
        <li>
          <Link
            href="/"
            className="flex items-center gap-1 text-[#52667E] hover:text-[#102A4C] transition-colors"
          >
            <Home className="w-3.5 h-3.5 text-[#3478F6]" />
            <span className="sr-only">Home</span>
          </Link>
        </li>

        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={index} className="flex items-center gap-1.5">
              <ChevronRight className="w-3.5 h-3.5 text-[#94A3B8] shrink-0" />
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className="font-medium text-[#52667E] hover:text-[#102A4C] transition-colors"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="font-semibold text-[#102A4C] truncate max-w-[200px] sm:max-w-none">
                  {item.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
