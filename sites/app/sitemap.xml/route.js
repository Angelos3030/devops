import { headers } from 'next/headers'
import { TRADES } from '../gia/[trade]/page'
import { APP_BASE } from '../../lib/appUrl'

export const dynamic = 'force-dynamic'   // multi-tenant: depends on the Host header

const APP_HOSTS = ['localhost', '127.0.0.1', 'getvitrina.gr', 'www.getvitrina.gr', 'app.getvitrina.gr']
const isAppHost = (h) =>
  APP_HOSTS.includes(h) || /\.(up\.railway\.app|railway\.app|vercel\.app|pages\.dev)$/.test(h)

const xml = (urls) =>
  `<?xml version="1.0" encoding="UTF-8"?>\n` +
  `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
  urls.map(({ loc, priority = '0.8', changefreq = 'monthly' }) =>
    `  <url><loc>${loc}</loc><changefreq>${changefreq}</changefreq><priority>${priority}</priority></url>`
  ).join('\n') +
  `\n</urlset>\n`

export function GET() {
  const host = (headers().get('host') || '').split(':')[0]

  // Το site του πελάτη είναι μονοσέλιδο — το sitemap του δείχνει το δικό του domain,
  // ποτέ τις δικές μας σελίδες.
  const urls = isAppHost(host)
    ? Object.keys(TRADES).map((t) => ({ loc: `${APP_BASE}/gia/${t}` }))
    : [{ loc: `https://${host}/`, priority: '1.0', changefreq: 'weekly' }]

  return new Response(xml(urls), {
    headers: { 'Content-Type': 'application/xml; charset=utf-8' },
  })
}
