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
    // The built-in optimizer (sharp/libvips, via /_next/image) is disabled.
    // It was the confirmed cause of the frontend's repeated OOM-kills:
    // processing a single large image through Next's request-handling path
    // cost ~130-170MB of native RSS, permanently, the first time any
    // distinct image+width+quality combination was requested - never
    // released, and unrelated to sharp/libvips itself (calling sharp
    // directly with identical operations on the same source cost ~15-25MB;
    // see deploy/cloudapps/README.md's memory-limit notes for the full
    // investigation). Trimming deviceSizes/imageSizes/minimumCacheTTL and
    // tuning libvips' own cache/concurrency settings were tried first and
    // measured to not meaningfully help - the excess lives in Next's own
    // server code, not anything tunable from here.
    unoptimized: true,
  },
};

export default nextConfig;
