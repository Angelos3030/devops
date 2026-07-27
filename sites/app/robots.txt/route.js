import { headers } from 'next/headers'
import { APP_BASE } from '../../lib/appUrl'

export const dynamic = 'force-dynamic'   // multi-tenant: depends on the Host header

const APP_HOSTS = ['localhost', '127.0.0.1', 'getvitrina.gr', 'www.getvitrina.gr', 'app.getvitrina.gr']
const isAppHost = (h) =>
  APP_HOSTS.includes(h) || /\.(up\.railway\.app|railway\.app|vercel\.app|pages\.dev)$/.test(h)

// Ένα robots.txt ανά domain. Ο πελάτης ΔΕΝ πρέπει να δείχνει στο δικό μας sitemap —
// αυτό θα έστελνε τη Google από το site του στις διαφημιστικές μας σελίδες.
export function GET() {
  const host = (headers().get('host') || '').split(':')[0]

  if (isAppHost(host)) {
    return new Response(
      ['User-Agent: *', 'Allow: /', 'Disallow: /preview/', 'Disallow: /choose/',
       'Disallow: /dashboard', '', `Sitemap: ${APP_BASE}/sitemap.xml`, ''].join('\n'),
      { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
    )
  }

  // Domain πελάτη: όλα ανοιχτά, δικό του sitemap.
  const base = `https://${host}`
  return new Response(
    ['User-Agent: *', 'Allow: /', '', `Sitemap: ${base}/sitemap.xml`, ''].join('\n'),
    { headers: { 'Content-Type': 'text/plain; charset=utf-8' } },
  )
}
