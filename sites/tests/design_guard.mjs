/**
 * ΟΛΑ ΤΑ TEMPLATES, ΣΕ ΠΡΑΓΜΑΤΙΚΟ BROWSER — για τα λάθη που δεν σπάνε τίποτα.
 *
 *   node tests/design_guard.mjs                    # στο ζωντανό
 *   node tests/design_guard.mjs --base http://localhost:3100
 *
 * Ο server απαντάει 200, το build περνάει, και το κουμπί είναι μαύρο πάνω σε
 * μαύρο. Ή το template ζητάει font που δεν κατεβάσαμε ποτέ και σερβίρεται σε
 * Arial. Κανένα από τα δύο δεν το πιάνει το scripts/e2e.py — τα πιάνει μόνο
 * κάτι που κοιτάζει τα pixels. Τρεις φορές μας ξέφυγε (Marble CTA, FindUs CTA,
 * Roboto Condensed)· γι' αυτό υπάρχει αυτό.
 *
 * Ελέγχει επίσης ότι καμία σελίδα πελάτη δεν χτυπάει Google/Meta και δεν γράφει
 * cookies — αυτό μας κρατάει χωρίς banner συγκατάθεσης.
 */
import { chromium } from 'playwright'
import { readFileSync } from 'node:fs'

// Η λίστα διαβάζεται από το registry, ΔΕΝ γράφεται με το χέρι — αλλιώς μένει πίσω
// σιωπηλά και τα νέα templates δεν ελέγχονται ποτέ (έγινε: έλειπαν 8).
const registry = readFileSync(new URL('../lib/templates/index.js', import.meta.url), 'utf8')
const keysLine = registry.match(/export const TEMPLATE_KEYS = \[([^\]]+)\]/)
if (!keysLine) throw new Error('Δεν βρέθηκε το TEMPLATE_KEYS στο lib/templates/index.js')
const TEMPLATES = [...keysLine[1].matchAll(/'([^']+)'/g)].map((m) => m[1])

const argIdx = process.argv.indexOf('--base')
const BASE = argIdx > -1 ? process.argv[argIdx + 1] : 'https://sites-production-da56.up.railway.app'
const TRACKERS = ['googleapis.com', 'gstatic.com', 'google-analytics.com',
  'googletagmanager.com', 'facebook.net', 'doubleclick.net']
const VH = 900

/**
 * Τρέχει ΜΕΣΑ στη σελίδα, για ό,τι φαίνεται εκείνη τη στιγμή στην οθόνη.
 * Γι' αυτό ο έλεγχος κάνει κύλιση: το elementsFromPoint δουλεύει μόνο για το
 * ορατό μέρος, αλλά είναι ο μόνος τρόπος να μάθεις τι υπάρχει ΠΡΑΓΜΑΤΙΚΑ από
 * πίσω — φωτογραφία hero, overlay, sticky nav. Το ανέβασμα στους γονείς λέει
 * ψέματα σε ακριβώς αυτές τις περιπτώσεις.
 */
function auditVisible() {
  const lum = (c) => {
    const [r, g, b] = c.map((v) => {
      v /= 255
      return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
    })
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
  }
  // Ο browser γυρίζει και rgb(12 34 56) και color(srgb .95 .92 .88 / .9) — το
  // δεύτερο σε κλίμακα 0-1. Αν το διαβάσεις σαν 0-255 βγάζει μαύρο και «βρίσκεις»
  // αόρατο κείμενο εκεί που δεν υπάρχει.
  const parse = (s) => {
    if (!s) return null
    const m = s.match(/[\d.]+/g)
    if (!m) return null
    const scale = s.startsWith('color(') ? 255 : 1
    return { rgb: m.slice(0, 3).map((v) => +v * scale), a: m[3] === undefined ? 1 : +m[3] }
  }

  // Ποιες οικογένειες έχουμε όντως κατεβάσει. Πιο αξιόπιστο από το
  // document.fonts.check, που κοιτάει αν ΦΟΡΤΩΘΗΚΕ το συγκεκριμένο βάρος και
  // βγάζει ψεύτικα λάθη με variable fonts.
  const shipped = new Set()
  for (const ss of document.styleSheets) {
    try {
      for (const r of ss.cssRules) {
        if (r.style && r.constructor.name === 'CSSFontFaceRule') {
          shipped.add(r.style.fontFamily.replace(/["']/g, '').trim())
        }
      }
    } catch { /* stylesheet άλλης προέλευσης — δεν μας αφορά */ }
  }
  const SYSTEM = /^(system-ui|sans-serif|serif|monospace|cursive|inherit|-apple-system|BlinkMacSystemFont|Georgia|Arial|Arial Narrow|Helvetica|Times New Roman|Courier New|ui-\w+)$/

  // Σπασμένες φωτογραφίες: το Unsplash σβήνει κατά καιρούς εικόνες και μένει
  // γκρι κουτί στο demo που βλέπει ο πελάτης. Το naturalWidth το λέει σίγουρα.
  const broken = [...document.querySelectorAll('img')]
    .filter((i) => i.complete && i.naturalWidth === 0)
    .map((i) => i.currentSrc || i.src).slice(0, 4)

  const invisible = [], missingFont = new Set()

  for (const el of document.querySelectorAll('a, button, h1, h2, h3, p, span, li')) {
    const box = el.getBoundingClientRect()
    if (box.width < 8 || box.height < 8) continue
    if (box.bottom < 0 || box.top > innerHeight) continue           // εκτός οθόνης
    const st = getComputedStyle(el)
    if (st.visibility === 'hidden' || st.opacity === '0') continue
    if (!el.textContent.trim()) continue
    if (el.closest('[aria-hidden="true"]')) continue                // διακοσμητικό
    // μόνο όποιος γράφει ο ίδιος το κείμενο, όχι τα κοντέινερ από πάνω του
    if ([...el.children].some((c) => c.textContent.trim() === el.textContent.trim())) continue

    const first = st.fontFamily.split(',')[0].replace(/["']/g, '').trim()
    if (first && !SYSTEM.test(first) && !shipped.has(first)) missingFont.add(first)

    // Τι υπάρχει από κάτω, με τη σειρά που το ζωγραφίζει ο browser.
    // Αν το κέντρο δεν είναι στην οθόνη, ΠΡΟΣΠΕΡΝΑΜΕ. (Παλιότερα το «στριμώχναμε»
    // στην άκρη, οπότε δειγματοληπτούσαμε τελείως άλλο στοιχείο και βγάζαμε
    // λευκό-σε-λευκό εκεί που υπήρχε φωτογραφία.) Η κύλιση το ξαναπιάνει.
    const x = box.left + box.width / 2
    const y = box.top + box.height / 2
    if (x < 1 || x > innerWidth - 1 || y < 1 || y > innerHeight - 1) continue
    const stack = document.elementsFromPoint(x, y)
    const idx = stack.indexOf(el)
    // ΑΠΟ το ίδιο το στοιχείο και κάτω, όχι από κάτω του: ένα <a> με δικό του
    // σκούρο φόντο (κουμπί) κρίνεται πάνω στο δικό του φόντο, όχι στης σελίδας.
    const under = idx === -1 ? stack : stack.slice(idx)

    // Υπάρχει ΟΠΟΥΔΗΠΟΤΕ εικόνα/βίντεο/gradient κάτω από το σημείο; Τότε δεν
    // κρίνουμε: δεν υπάρχει ΕΝΑ χρώμα να συγκρίνεις, και λευκά γράμματα πάνω σε
    // φωτογραφία διαβάζονται μια χαρά.
    // Η σειρά της στοίβας ΔΕΝ είναι σειρά ζωγραφίσματος — ένα <img> εμφανίζεται
    // μετά τον γονιό του αλλά ζωγραφίζεται ΠΑΝΩ από το φόντο του. Γι' αυτό
    // κοιτάμε όλη τη στοίβα πριν διαλέξουμε χρώμα, αλλιώς «βρίσκουμε» λευκό
    // πάνω σε λευκό εκεί που στην οθόνη υπάρχει φωτογραφία.
    if (under.some((n) => /^(IMG|VIDEO|CANVAS|svg)$/.test(n.tagName) ||
                          getComputedStyle(n).backgroundImage !== 'none')) continue

    let bg = null
    for (const n of under) {
      const c = parse(getComputedStyle(n).backgroundColor)
      if (c && c.a > 0.85) { bg = c.rgb; break }
    }
    if (!bg) continue

    const fg = parse(st.color)
    if (!fg) continue
    const text = el.textContent.trim().slice(0, 40)
    if (fg.a < 0.12) {
      invisible.push({ tag: el.tagName, text, ratio: 'διάφανο' })
      continue
    }
    // Κάτω από 3:1 δεν διαβάζεται ούτε σε μεγάλα γράμματα — δεν είναι θέμα
    // γούστου. (Το WCAG AA θέλει 4.5 για μικρά· κρατάμε 3 ώστε να μη χτυπάει
    // σε σκόπιμα απαλά διακοσμητικά.)
    const L1 = lum(fg.rgb), L2 = lum(bg)
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05)
    if (ratio < 3) invisible.push({ tag: el.tagName, text, ratio: ratio.toFixed(2) })
  }
  return { invisible, missingFont: [...missingFont], broken }
}

const run = async () => {
  console.log('='.repeat(64))
  console.log(`VITRINA — έλεγχος εμφάνισης, ${TEMPLATES.length} templates`)
  console.log(BASE)
  console.log('='.repeat(64) + '\n')

  const problems = []
  const browser = await chromium.launch()

  for (const t of TEMPLATES) {
    const ctx = await browser.newContext({ locale: 'el-GR', viewport: { width: 1440, height: VH } })
    const page = await ctx.newPage()
    const ext = new Set()
    page.on('request', (r) => {
      const h = new URL(r.url()).hostname
      if (TRACKERS.some((x) => h.endsWith(x))) ext.add(h)
    })

    try {
      await page.goto(`${BASE}/preview/${t}?biz=taverna`, { waitUntil: 'networkidle', timeout: 45000 })
      await page.waitForTimeout(400)

      const height = await page.evaluate(() => document.body.scrollHeight)
      const seen = new Map(), fonts = new Set(), broken = new Set()
      for (let y = 0; y < height; y += VH * 0.85) {
        await page.evaluate((v) => window.scrollTo(0, v), y)
        await page.waitForTimeout(180)
        const res = await page.evaluate(auditVisible)
        res.invisible.forEach((v) => seen.set(`${v.tag}|${v.text}`, v))
        res.missingFont.forEach((f) => fonts.add(f))
        res.broken.forEach((b) => broken.add(b))
      }

      const invisible = [...seen.values()]
      const cookies = await ctx.cookies()
      const bad = []
      if (invisible.length) bad.push(`αόρατο κείμενο ×${invisible.length}`)
      if (fonts.size) bad.push(`fonts που δεν κατεβάσαμε: ${[...fonts].join(', ')}`)
      if (broken.size) bad.push(`σπασμένες φωτογραφίες ×${broken.size}`)
      if (ext.size) bad.push(`εξωτερικά αιτήματα: ${[...ext].join(', ')}`)
      if (cookies.length) bad.push(`cookies: ${cookies.length}`)

      console.log(`  ${bad.length ? '✗' : '✓'} ${t.padEnd(11)} ${bad.join(' | ') || 'καθαρό'}`)
      invisible.slice(0, 6).forEach((v) =>
        console.log(`      └ <${v.tag.toLowerCase()}> «${v.text}» αντίθεση ${v.ratio}`))
      if (bad.length) problems.push(`${t}: ${bad.join(' | ')}`)
    } catch (e) {
      console.log(`  ✗ ${t.padEnd(11)} ${e.message.split('\n')[0]}`)
      problems.push(`${t}: ${e.message.split('\n')[0]}`)
    }
    await ctx.close()
  }
  await browser.close()

  console.log('\n' + '='.repeat(64))
  if (problems.length) {
    console.log(`❌ ${problems.length} templates με πρόβλημα:`)
    problems.forEach((p) => console.log(`   • ${p}`))
    process.exit(1)
  }
  console.log('✅ Όλα διαβάζονται, όλα τα fonts υπάρχουν, τίποτα δεν φεύγει προς τα έξω.')
}

run()
