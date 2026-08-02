/**
 * Vitrina tenant router — Cloudflare Worker.
 *
 * Γιατί υπάρχει: το Railway δρομολογεί με βάση το Host header και γυρνάει 404 σε
 * κάθε host που δεν είναι δηλωμένος στο service. Το Hobby plan δέχεται 2 custom
 * domains ανά service, οπότε ο 2ος πελάτης δεν μπορούσε να βγει live — και το
 * Cloudflare for SaaS δεν το λύνει, γιατί διατηρεί το Host του πελάτη.
 *
 * Τι κάνει: δέχεται την κίνηση του domain του πελάτη, τη στέλνει στο Railway με το
 * Host που το Railway αναγνωρίζει, και περνάει το πραγματικό domain σε header
 * (`x-tenant-host`), που το διαβάζει το middleware του Next.js.
 *
 * Αποτέλεσμα: απεριόριστα domain πελατών, χωρίς custom domain στο Railway.
 *
 * Deploy: python scripts/deploy_worker.py
 */

const ORIGIN = 'sites-production-da56.up.railway.app'

export default {
  async fetch(request) {
    const url = new URL(request.url)
    const tenantHost = url.hostname          // π.χ. taverna-o-mitsos.gr

    url.hostname = ORIGIN
    url.protocol = 'https:'
    url.port = ''

    const headers = new Headers(request.headers)
    headers.set('Host', ORIGIN)              // ώστε το Railway να δεχτεί το αίτημα
    headers.set('x-tenant-host', tenantHost) // ώστε το app να ξέρει ποιανού site είναι
    headers.set('x-forwarded-host', tenantHost)
    headers.set('x-forwarded-proto', 'https')

    const upstream = new Request(url.toString(), {
      method: request.method,
      headers,
      body: request.method === 'GET' || request.method === 'HEAD' ? undefined : request.body,
      redirect: 'manual',
    })

    const res = await fetch(upstream)

    // Τυχόν redirect προς το origin ξαναγράφεται στο domain του πελάτη, ώστε να μη
    // «διαρρέει» ποτέ το railway.app URL στη γραμμή διευθύνσεων.
    const loc = res.headers.get('location')
    if (loc && loc.includes(ORIGIN)) {
      const out = new Headers(res.headers)
      out.set('location', loc.replace(ORIGIN, tenantHost))
      return new Response(res.body, { status: res.status, headers: out })
    }
    return res
  },
}
