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
        transform:none!important;animation:none!important;transition:none!important}
        /* Τα παραπάνω είναι ονόματα κλάσεων των wow.js/AOS. Τα ΣΥΓΧΡΟΝΑ
           scroll-driven animations (animation-timeline: view()) μπαίνουν σε
           οποιαδήποτε κλάση CSS module, οπότε καμία λίστα ονομάτων δεν τα
           πιάνει. Μετρήθηκε στο AegisDental: οι τέσσερις κάρτες υπηρεσιών
           υπήρχαν με σωστό κείμενο και μέγεθος 604x165, αλλά φωτογραφήθηκαν με
           opacity 0 — γιατί το scroll loop γυρίζει στην κορυφή πριν τη λήψη και
           το view() ξαναμηδενίζεται. Η σελίδα έβγαινε ΚΕΝΗ και καθαρή σε κάθε
           μετρική. Καθολικός μηδενισμός: κάθε στοιχείο αποτυπώνεται στην
           κατάσταση ηρεμίας του, που είναι και η κατάσταση που βλέπει όποιος
           έχει prefers-reduced-motion. */
        *,*::before,*::after{animation:none!important;transition:none!important}`,
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
      // Διπλή ΠΡΟΒΕΒΛΗΜΕΝΗ επικεφαλίδα σε ΓΕΙΤΟΝΙΚΕΣ ενότητες. Συντηρητικό:
      // μόνο ορατά h2/h3, μόνο διαδοχικές εμφανίσεις, χωρίς nav/CTA/aria.
      // Μετρήθηκε στο Gymso: «Εδώ δεν είσαι συνδρομή» δύο φορές στη σειρά.
      duplicateHeadings: (() => {
        const seen = [...document.querySelectorAll('h2,h3')]
          .filter((e) => e.offsetParent !== null && !e.closest('nav,header,footer'))
          .map((e) => e.textContent.trim().replace(/\s+/g, ' '))
          .filter((x) => x.split(' ').length >= 3)
        const dup = []
        for (let i = 1; i < seen.length; i++) {
          if (seen[i] && seen[i] === seen[i - 1]) dup.push(seen[i].slice(0, 60))
        }
        return [...new Set(dup)]
      })(),
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
          if (!spills) return false
          // ΠΡΟΕΞΟΧΗ ≠ ΑΠΩΛΕΙΑ. Αν ΚΑΝΕΝΑΣ πρόγονος δεν κόβει αυτόν τον άξονα
          // και η σελίδα δεν κυλά οριζόντια, το περιεχόμενο είναι ΟΡΑΤΟ — άρα
          // σχέδιο, όχι σφάλμα. Μετρήθηκε στο clean-work: μπλε κάρτα τηλεφώνου
          // ακουμπισμένη σκόπιμα 20px έξω από τη γωνία της φωτογραφίας, όπως
          // στο πρωτότυπο. Ο έλεγχος υπάρχει για περιεχόμενο που ΧΑΝΕΤΑΙ (στο
          // Frost η σειρά γεύσεων κοβόταν μέσα σε container με overflow:hidden),
          // όχι για κάθε στοιχείο που ξεπερνά το πλαίσιο του γονέα του.
          for (let n = e; n; n = n.parentElement) {
            const c = getComputedStyle(n).overflowX
            // ΚΥΛΙΟΜΕΝΟΣ πρόγονος ≠ πρόγονος που ΚΟΒΕΙ. Το `auto`/`scroll`
            // σημαίνει ότι ο χρήστης ΦΤΑΝΕΙ το περιεχόμενο — carousel με
            // scroll-snap, ακριβώς το μοτίβο που ζητά το brief αλληλεπίδρασης.
            // Μετρήθηκε στο AegisDental: το εσωτερικό .sliderTrack αναφερόταν
            // ως υπερχείλιση 4482px επειδή ο κυλιόμενος γονέας μετρούσε σαν
            // να έκρυβε. Κάθε theme με slider θα χτυπούσε.
            if (c === 'auto' || c === 'scroll') return false
            if (c === 'hidden' || c === 'clip') return true
          }
          return document.documentElement.scrollWidth >
                 document.documentElement.clientWidth
        })
        .slice(0, 5)
        .map((e) => `${e.tagName.toLowerCase()}.${(e.className || '').toString().split(' ')[0]} +${e.scrollWidth - e.clientWidth}px`),
      // ΑΠΟΚΟΜΜΕΝΟ ΠΕΡΙΕΧΟΜΕΝΟ ≠ ΥΠΕΡΧΕΙΛΙΣΗ. Το innerOverflow βλέπει ό,τι
      // ΞΕΦΕΥΓΕΙ από το πλαίσιο· δεν βλέπει ό,τι το πλαίσιο ΚΟΒΕΙ. Μετρήθηκε
      // στο klassy-cafe: κάρτα χάρτη 144x90 με περιεχόμενο 134px — το κείμενο
      // «Φορτώνει από την Google…» και ο σύνδεσμος «κατευθείαν οδηγίες» ήταν
      // κρυμμένα, με overflow=0, innerOverflow=[] και όλες τις πύλες πράσινες.
      //
      // ΔΕΝ αρκεί scrollHeight > clientHeight. Αυτό το πληρούν και σκιές,
      // transforms και ::after. Απαιτούμε ΠΡΑΓΜΑΤΙΚΟ απόγονο ΜΕ ΚΕΙΜΕΝΟ που
      // κόβεται — το ίδιο μάθημα με το CSS τρίγωνο του Medic Care.
      clipped: (() => {
        const themeRoot = document.querySelector('[class*="_root__"]')
        const themePrefix = themeRoot
          ? (themeRoot.className.toString().match(/([A-Za-z]+)_root__/) || [])[1] || ''
          : ''
        const prefixOf = (el) => {
          const c = (el.className || '').toString().split(' ')[0]
          const m = c.match(/^([A-Za-z]+)_/)
          return m ? m[1] : ''
        }
        const out = []
        for (const el of document.querySelectorAll('div,section,a,button,p,li,figure')) {
          const cs = getComputedStyle(el)
          const hidesY = cs.overflowY === 'hidden' || cs.overflowY === 'clip'
          const hidesX = cs.overflowX === 'hidden' || cs.overflowX === 'clip'
          if (!hidesY && !hidesX) continue
          if (cs.webkitLineClamp && cs.webkitLineClamp !== 'none') continue  // σκόπιμη περικοπή
          if (cs.visibility === 'hidden' || cs.display === 'none') continue
          const cutY = hidesY ? el.scrollHeight - el.clientHeight : 0
          const cutX = hidesX ? el.scrollWidth - el.clientWidth : 0
          if (cutY <= 8 && cutX <= 8) continue
          const box = el.getBoundingClientRect()
          // Ποιο ΠΡΑΓΜΑΤΙΚΟ κείμενο χάνεται· χωρίς αυτό δεν υπάρχει εύρημα.
          const cut = []
          for (const c of el.querySelectorAll('*')) {
            const txt = (c.textContent || '').trim()
            if (!txt || c.children.length) continue          // μόνο φύλλα με κείμενο
            if (c.closest('[aria-hidden="true"]')) continue   // διακοσμητικό
            const r = c.getBoundingClientRect()
            if (!r.width || !r.height) continue
            const by = Math.round(Math.max(r.bottom - box.bottom, box.top - r.top,
                                           r.right - box.right, box.left - r.left))
            if (by > 2) cut.push({ text: txt.slice(0, 34), by })
          }
          if (!cut.length) continue                           // σκιά/transform/::after
          let target = ''
          for (let n = el; n; n = n.parentElement) {
            if (themePrefix && prefixOf(n) === themePrefix) {
              target = (n.className || '').toString().split(' ')[0].replace(/__.*$/, '')
              break
            }
          }
          out.push({
            sel: (el.className || '').toString().split(' ')[0].replace(/__.*$/, ''),
            owner: prefixOf(el), themeOwner: themePrefix, target,
            clientH: el.clientHeight, scrollH: el.scrollHeight,
            hidden: Math.max(cutY, cutX), axis: cutY > cutX ? 'ύψος' : 'πλάτος',
            overflow: `${cs.overflowX}/${cs.overflowY}`,
            cut: cut.sort((a, b) => b.by - a.by).slice(0, 3),
          })
          if (out.length >= 5) break
        }
        return out
      })(),
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
