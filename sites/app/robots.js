// Allow indexing of client sites; keep demo/preview pages out of the index.
export default function robots() {
  return {
    rules: { userAgent: '*', allow: '/', disallow: ['/preview/'] },
  }
}
