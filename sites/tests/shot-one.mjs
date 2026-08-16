// Αποτύπωση ΕΝΟΣ στόχου σε 1440 και 390 — κοινή για πρωτότυπο και Vitrina.
//
//   node tests/shot-one.mjs <root|http://…> <entry> <tag> <outDir>
//
// Αν το <root> ξεκινά με http, το <entry> είναι διαδρομή στον ζωντανό server.
// Αλλιώς σερβίρεται στατικά ο φάκελος <root> (σχετικά με το repo root).
//
// Τα animations εξουδετερώνονται ΠΡΙΝ τη λήψη: wow.js/AOS κρατούν opacity:0 και
// το fullPage screenshot γυρίζει στην κορυφή πριν προλάβουν να ενεργοποιηθούν.
// Μετρήθηκε στο Gymso Fitness — χωρίς αυτό βγαίνει «κενή σελίδα» και κρίνεται
// σπασμένο κάτι που δεν είναι.
import { chromium } from 'playwright'
import { createServer } from 'node:http'
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { extname, join, resolve } from 'node:path'

const [root, entry, tag, outDir] = process.argv.slice(2)
if (!root || !entry || !tag || !outDir) {
  console.error('usage: shot-one.mjs <root|url> <entry> <tag> <outDir>')
  process.exit(2)
}
const MIME = {
  '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff': 'font/woff',
  '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.otf': 'font/otf', '.mp4': 'video/mp4',
  '.eot': 'application/vnd.ms-fontobject', '.avif': 'image/avif',
}
const safe = (u) => decodeURIComponent(u.split('?')[0].split('#')[0])
  .split(/[/\\]+/).filter((x) => x && x !== '..' && x !== '.').join('/')

const live = root.startsWith('http')
let srv = null
let base = root
if (!live) {
  const dir = resolve(process.cwd(), '..', root)
  srv = createServer(async (req, res) => {
    try {
      const buf = await readFile(join(dir, safe(req.url)))
      res.writeHead(200, { 'Content-Type': MIME[extname(req.url.split('?')[0]).toLowerCase()] || 'application/octet-stream' })
      res.end(buf)
    } catch { res.writeHead(404); res.end('not found') }
  })
  await new Promise((r) => srv.listen(4611, r))
  base = 'http://127.0.0.1:4611'
}

await mkdir(outDir, { recursive: true })
const b = await chromium.launch()
const out = { tag }
let failed = false

for (const [label, w, h] of [['desktop', 1440, 1024], ['mobile', 390, 844]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h } })
  const pg = await ctx.newPage()
  const errs = []
  pg.on('console', (m) => m.type() === 'error' && errs.push(m.text().slice(0, 160)))
  pg.on('pageerror', (e) => errs.push(String(e).slice(0, 160)))
  try {
    await pg.goto(`${base}/${entry}`.replace(/([^:])\/\//g, '$1/'), { waitUntil: 'load', timeout: 60000 })
    await pg.addStyleTag({
      content: `[data-aos],.wow,.animate-box,.fadeIn,.fadeInUp,.fadeInLeft,.fadeInRight,
        .animated,.reveal,[class*="animate__"]{opacity:1!important;visibility:visible!important;
        transform:none!important;animation:none!important;transition:none!important}`,
    })
    await pg.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 600) {
        window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 80))
      }
      window.scrollTo(0, 0)
      await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 3000))])
      await Promise.all([...document.images].map((i) => Promise.race([
        i.decode().catch(() => {}), new Promise((r) => setTimeout(r, 2500)),
      ])))
    })
    await pg.waitForTimeout(700)
    out[label] = await pg.evaluate(() => ({
      height: document.body.scrollHeight,
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      images: document.images.length,
      broken: [...document.images].filter((i) => i.complete && i.naturalWidth === 0).length,
      h1: document.querySelectorAll('h1').length,
      smallTaps: [...document.querySelectorAll('a,button')]
        .filter((e) => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.height < 44 || r.width < 44) }).length,
      // Εσωτερική υπερχείλιση: το document μπορεί να μην κυλά οριζόντια ενώ
      // μια σειρά καρτών κόβεται μέσα στο container της. Στο Frost η σειρά
      // γεύσεων έβγαινε κομμένη και στις δύο άκρες με overflow=0 στο document.
      innerOverflow: [...document.querySelectorAll('div,section,ul,main')]
        .filter((e) => {
          if (e.scrollWidth - e.clientWidth <= 4) return false
          const ox = getComputedStyle(e).overflowX
          if (ox === 'auto' || ox === 'scroll') return false // σκόπιμο scroll
          // ΔΙΑΚΟΣΜΗΤΙΚΗ ΠΡΟΕΞΟΧΗ ≠ ΣΠΑΣΜΕΝΗ ΔΙΑΤΑΞΗ.
          // Μετρήθηκε στο Medic Care: το h3::after είναι CSS τρίγωνο
          // (right:-10px, border-width:10px 0 10px 10px) — το βελάκι της
          // ετικέτας του πρωτοτύπου. Έδινε +10px «υπερχείλιση» σε κάθε γύρο,
          // το μοντέλο το κυνηγούσε επί τέσσερα τρεξίματα και χάλαγε το mobile.
          // Αν ΚΑΝΕΝΑΣ πραγματικός απόγονος δεν ξεπερνά το πλαίσιο, η
          // υπερχείλιση προέρχεται από ::before/::after και είναι σχέδιο.
          const box = e.getBoundingClientRect()
          const limit = box.left + e.clientWidth + 2
          const spills = [...e.querySelectorAll('*')]
            .some((c) => c.getBoundingClientRect().right > limit)
          return spills
        })
        .slice(0, 5)
        .map((e) => `${e.tagName.toLowerCase()}.${(e.className || '').toString().split(' ')[0]} +${e.scrollWidth - e.clientWidth}px`),
    }))
    out[label].consoleErrors = errs.length
    out[label].errorSamples = errs.slice(0, 3)
    await pg.screenshot({ path: join(outDir, `${tag}-${label}.png`), fullPage: true })
  } catch (e) {
    failed = true
    out[label] = { fail: String(e).slice(0, 200) }
  }
  await ctx.close()
}
await b.close()
if (srv) srv.close()
await writeFile(join(outDir, `${tag}-metrics.json`), JSON.stringify(out, null, 1))
console.log(JSON.stringify(out))
process.exit(failed ? 1 : 0)
