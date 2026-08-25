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
  },
};

export default nextConfig;
