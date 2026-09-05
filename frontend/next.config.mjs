/** @type {import('next').NextConfig} */
const nextConfig = {
  // Force rebuild on Jan 12 to clear stale build cache
  // Vercel cache issue: error pointed to old code, rebuild required
};

export default nextConfig;
