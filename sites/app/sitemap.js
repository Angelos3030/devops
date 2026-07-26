import { TRADES } from './gia/[trade]/page'

// Only the ad landings are indexable app pages (client sites live on their own domains).
export default function sitemap() {
  const base = 'https://app.getvitrina.gr'
  const now = new Date()
  return Object.keys(TRADES).map((trade) => ({
    url: `${base}/gia/${trade}`,
    lastModified: now,
    changeFrequency: 'monthly',
    priority: 0.8,
  }))
}
