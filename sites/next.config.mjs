/** @type {import('next').NextConfig} */

// Βασικά security headers. Το HSTS λέει στους browsers «μόνο HTTPS» και το
// nosniff/frame-options κλείνουν κλασικές επιθέσεις. Δεν βάζουμε CSP εδώ: τα
// templates φορτώνουν Google Fonts/Maps και εικόνες πελατών, οπότε μια λάθος
// CSP θα έσπαγε ζωντανά site.
const securityHeaders = [
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'geolocation=(), microphone=(), camera=()' },
]

const nextConfig = {
  images: { unoptimized: true }, // static hosting friendly (Cloudflare Pages)
  eslint: { ignoreDuringBuilds: true },
  poweredByHeader: false,
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }]
  },
}
export default nextConfig
