/** @type {import('next').NextConfig} */
const nextConfig = {
  images: { unoptimized: true }, // static hosting friendly (Cloudflare Pages)
  eslint: { ignoreDuringBuilds: true },
}
export default nextConfig
