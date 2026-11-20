import { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://gokulsastrology.com";
  const currentDate = new Date();

  const routes = [
    { url: "", changeFrequency: "daily" as const, priority: 1.0 },
    { url: "/tools", changeFrequency: "weekly" as const, priority: 0.9 },
    { url: "/tools/horoscope", changeFrequency: "weekly" as const, priority: 0.9 },
    { url: "/tools/advanced-kp", changeFrequency: "weekly" as const, priority: 0.8 },
    { url: "/tools/numerology", changeFrequency: "weekly" as const, priority: 0.8 },
    { url: "/tools/marriage-compatibility", changeFrequency: "weekly" as const, priority: 0.8 },
    { url: "/tools/panchang", changeFrequency: "daily" as const, priority: 0.8 },
    { url: "/tools/muhurta", changeFrequency: "daily" as const, priority: 0.8 },
    { url: "/tools/ashtakavarga", changeFrequency: "monthly" as const, priority: 0.7 },
    { url: "/disclaimer", changeFrequency: "monthly" as const, priority: 0.5 },
    { url: "/terms", changeFrequency: "monthly" as const, priority: 0.5 },
    { url: "/privacy", changeFrequency: "monthly" as const, priority: 0.5 },
    { url: "/refund-policy", changeFrequency: "monthly" as const, priority: 0.5 },
    { url: "/contact", changeFrequency: "monthly" as const, priority: 0.6 },
  ];

  return routes.map((route) => ({
    url: `${baseUrl}${route.url}`,
    lastModified: currentDate,
    changeFrequency: route.changeFrequency,
    priority: route.priority,
  }));
}
