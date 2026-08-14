import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@daliang/db", "@daliang/shared"],
};

export default nextConfig;
