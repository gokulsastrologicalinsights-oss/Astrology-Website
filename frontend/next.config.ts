import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: [
    "127.0.0.1",
    "localhost",
    "127.0.0.1:3000",
    "localhost:3000",
    "127.0.0.1:3001",
    "localhost:3001",
  ],
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      "http://127.0.0.1:8000";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/kp-events-prediction",
        destination: "/tools/kp-events-prediction",
        permanent: false,
      },
      {
        source: "/kp-events",
        destination: "/tools/kp-events-prediction",
        permanent: false,
      },
      {
        source: "/kp-prediction",
        destination: "/tools/kp-events-prediction",
        permanent: false,
      },
      {
        source: "/tools/kp-prediction",
        destination: "/tools/kp-events-prediction",
        permanent: false,
      },
      {
        source: "/events-prediction",
        destination: "/tools/kp-events-prediction",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;
