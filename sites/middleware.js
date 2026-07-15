import { NextResponse } from 'next/server'

// Multi-tenant routing: custom client domains → render that client's site.
// The app's own hosts pass through untouched.
const APP_HOSTS = ['localhost', '127.0.0.1', 'getvitrina.gr', 'www.getvitrina.gr', 'app.getvitrina.gr']

export function middleware(req) {
  const host = (req.headers.get('host') || '').split(':')[0]
  const { pathname } = req.nextUrl
  const isApp =
    APP_HOSTS.includes(host) ||
    host.endsWith('.up.railway.app') ||   // Railway-generated domains (our own app)
    host.endsWith('.railway.app') ||
    host.endsWith('.vercel.app') ||
    host.endsWith('.pages.dev')
  const isInternal =
    pathname.startsWith('/site') || pathname.startsWith('/preview') ||
    pathname.startsWith('/_next') || pathname.startsWith('/api') ||
    pathname === '/favicon.ico' || pathname === '/robots.txt' || pathname === '/sitemap.xml'

  if (isApp || isInternal) return NextResponse.next()

  // Custom client domain (e.g. koutrakiskouzines.gr) → render its site.
  // The backend /clients/{id}/site-data resolves the host as a domain.
  const url = req.nextUrl.clone()
  url.pathname = `/site/${host}`
  return NextResponse.rewrite(url)
}

export const config = { matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'] }
