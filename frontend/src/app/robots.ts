import { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://gokulsastrology.com";

  return {
    rules: [
      {
        userAgent: "*",
        allow: [
          "/",
          "/tools",
          "/tools/horoscope",
          "/tools/numerology",
          "/tools/ashtakavarga",
          "/tools/panchang",
          "/tools/muhurta",
          "/disclaimer",
          "/terms",
          "/privacy",
          "/refund-policy",
          "/contact",
        ],
        disallow: [
          "/api/",
          "/dashboard/",
          "/admin/",
          "/update-password/",
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
