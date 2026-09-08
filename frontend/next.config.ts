import type { NextConfig } from "next";
import path from "path";

function getApiOrigin(): string | undefined {
  const raw = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "");
  if (!raw) return undefined;
  return raw.endsWith("/api") ? raw.slice(0, -4) : raw;
}

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname, "../"),
  async rewrites() {
    const apiOrigin = getApiOrigin();
    if (!apiOrigin) return [];

    return [
      {
        source: "/api/:path*",
        destination: `${apiOrigin}/api/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "images.unc.edu",
      },
    ],
    // Defaults (8 deviceSizes x 8 imageSizes) generate a lot of distinct
    // sharp-optimized variants per source image, each re-processed after
    // the cache TTL expires. On a small site this is the main driver of
    // the frontend's memory growth (see deploy/cloudapps/README.md's
    // memory-limit notes) - fewer buckets and a longer cache TTL trade a
    // little responsive-image granularity for a much smaller working set.
    deviceSizes: [640, 828, 1080, 1920, 3840],
    imageSizes: [64, 96, 128, 192, 256, 384],
    minimumCacheTTL: 60 * 60 * 24,
  },
};

export default nextConfig;
