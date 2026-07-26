// Allow indexing of client sites + /gia ad landings; keep raw previews out.
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/preview/', '/choose/'] },
    sitemap: 'https://app.getvitrina.gr/sitemap.xml',
  }
}
