// Allow indexing of client sites + /gia ad landings; keep raw previews out.
import { APP_BASE } from '../lib/appUrl'

export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/preview/', '/choose/', '/dashboard'] },
    sitemap: `${APP_BASE}/sitemap.xml`,
  }
}
