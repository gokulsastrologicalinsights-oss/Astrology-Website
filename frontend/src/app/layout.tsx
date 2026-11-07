import { Suspense } from "react";
import type { Metadata } from "next";
import { Inter, Noto_Sans_Tamil, Cinzel } from "next/font/google";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n";
import { AuthProvider } from "@/lib/auth-context";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const notoTamil = Noto_Sans_Tamil({
  variable: "--font-tamil",
  subsets: ["tamil"],
  display: "swap",
});

const cinzel = Cinzel({
  variable: "--font-cinzel",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Gokul's Astrological Insights — Precision Vedic & KP Astronomical System",
  description:
    "Deterministic sidereal Vedic and KP Krishnamurti Paddhati astrological calculations powered by the XALEN astronomical engine.",
  keywords: [
    "Gokul's Astrological Insights",
    "Vedic Astrology",
    "KP Astrology",
    "Krishnamurti Paddhati",
    "Vimshottari Dasa",
    "Tamil Astrology",
    "Jathagam",
    "XALEN ephemeris",
  ],
  icons: {
    icon: [
      { url: "/favicon.ico" },
      { url: "/icon.png", sizes: "512x512", type: "image/png" },
    ],
    apple: [
      { url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" },
    ],
  },
  openGraph: {
    title: "Gokul's Astrological Insights — Precision Vedic & KP Astronomical System",
    description:
      "Deterministic sidereal Vedic and KP Krishnamurti Paddhati astrological calculations powered by the XALEN astronomical engine.",
    siteName: "Gokul's Astrological Insights",
    type: "website",
    images: [
      {
        url: "/logo.png",
        width: 1024,
        height: 1024,
        alt: "Gokul's Astrological Insights Logo",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Gokul's Astrological Insights — Precision Vedic & KP Astronomical System",
    description:
      "Deterministic sidereal Vedic and KP Krishnamurti Paddhati astrological calculations powered by the XALEN astronomical engine.",
    images: ["/logo.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${notoTamil.variable} ${cinzel.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#F2F3F5] text-[#183047]">
        <LanguageProvider>
          <AuthProvider>
            <div className="flex flex-col min-h-screen">
              <Suspense fallback={<div className="h-14 bg-white border-b border-[#D9DEE7]" />}>
                <Navbar />
              </Suspense>
              <main className="flex-1 w-full">{children}</main>
              <Suspense fallback={<div className="h-16 bg-[#F7F4EE] border-t border-[#E2DCD5]" />}>
                <Footer />
              </Suspense>
            </div>
          </AuthProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
