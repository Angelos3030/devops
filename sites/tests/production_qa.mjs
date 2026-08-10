#!/usr/bin/env node
/**
 * Production QA — τρέχει ΜΕΤΑ από κάθε deploy.
 *
 *   node sites/tests/production_qa.mjs                      # getvitrina.gr
 *   node sites/tests/production_qa.mjs --url http://localhost:8899/index.html
 *   node sites/tests/production_qa.mjs --skip-lighthouse    # γρήγορο πέρασμα
 *
 * Δύο ανεξάρτητα επίπεδα, κανένα δεν αντικαθιστά το άλλο:
 *
 *   1. Playwright — συμπεριφορά. Πιάνει πράγματα που το Lighthouse δεν βλέπει:
 *      hover/focus, reduced motion, τη ροή του prompt, σπασμένες εικόνες μετά
 *      από decode(), κενά iframes.
 *   2. Lighthouse — μετρήσιμη ποιότητα. Performance, accessibility, best
 *      practices, SEO, Core Web Vitals.
 *
 * Κάθε έλεγχος εδώ υπάρχει επειδή ΚΑΤΙ ΕΣΠΑΣΕ μία φορά. Μη βγάλεις κανέναν
 * χωρίς να ξέρεις ποιο bug έπαψε να είναι δυνατό.
 */
import { chromium } from 'playwright'

const args = process.argv.slice(2)
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`)
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback
}
const PAGE = flag('url', 'https://getvitrina.gr/')
const SKIP_LH = args.includes('--skip-lighthouse')
const SITES = 'https://sites-production-da56.up.railway.app'

// Τα thresholds αφήνουν περιθώριο για τη διακύμανση του Lighthouse (±5 μονάδες
// μεταξύ εκτελέσεων). Στόχος: να πιάνουμε ΟΠΙΣΘΟΔΡΟΜΗΣΕΙΣ, όχι να κυνηγάμε 100άρια.
const LH = {
  mobile:  { performance: 85, accessibility: 95, 'best-practices': 95, seo: 95 },
  desktop: { performance: 95, accessibility: 95, 'best-practices': 95, seo: 95 },
}
// Core Web Vitals — μόνο όσα μετριούνται αξιόπιστα σε lab. Το Speed Index
// εξαρτάται πολύ από το δίκτυο της στιγμής, οπότε αναφέρεται χωρίς όριο.
const VITALS = {
  mobile:  { 'largest-contentful-paint': 2500, 'cumulative-layout-shift': 0.05, 'total-blocking-time': 350 },
  desktop: { 'largest-contentful-paint': 1500, 'cumulative-layout-shift': 0.05, 'total-blocking-time': 150 },
}

const DEMOS = [
  'warmth?biz=taverna', 'bakery-editorial?biz=cafe', 'beauty-atelier?biz=salon',
  'clinic-triage?biz=dentist', 'marble?biz=lawyer', 'aegean?biz=rooms',
]

// Δύο βαθμίδες, γιατί δεν είναι όλες οι αποτυχίες ίδιες:
//
//   critical — accessibility, SEO, σπασμένα αιτήματα, console errors, εγγραφές
//              στη βάση, overflow, βασική ροή. Το deploy θεωρείται ΑΠΟΤΥΧΗΜΕΝΟ.
//   perf     — σκορ και χρόνοι. Κυμαίνονται μεταξύ εκτελέσεων, οπότε πέφτουν
//              κάτω από κατώφλι αντί για απόλυτο 100. Θέλουν προσοχή, όχι rollback.
//
// Έξοδος: 0 καθαρό · 1 κρίσιμη αποτυχία · 2 μόνο επιδόσεις κάτω από το όριο.
const pass = [], failCritical = [], failPerf = []
const check = (ok, label, detail = '', kind = 'critical') => {
  if (ok) pass.push(label)
  else (kind === 'perf' ? failPerf : failCritical).push(`${label}${detail ? ` (${detail})` : ''}`)
  const mark = ok ? '✓' : (kind === 'perf' ? '!' : '✗')
  console.log(`  ${mark} ${label}${detail ? `  — ${detail}` : ''}`)
}
const head = (t) => console.log(`\n${t}`)

// ───────────────────────────────────────────────────────── Playwright
async function behaviour(browser) {
  for (const [width, height, name] of [[1440, 1024, 'desktop'], [768, 1024, 'tablet'], [390, 844, 'mobile']]) {
    head(`[${name} ${width}×${height}]`)
    const ctx = await browser.newContext({
      viewport: { width, height }, deviceScaleFactor: 1,
      isMobile: width < 500, hasTouch: width < 500,
    })
    const page = await ctx.newPage()
    const errors = [], failed = []
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text().slice(0, 110)))
    page.on('response', (r) => { if (r.status() >= 400) failed.push(`${r.status()} ${r.url().slice(-55)}`) })
    await page.addInitScript(() => {
      window.__cls = 0
      new PerformanceObserver((l) => {
        for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value
      }).observe({ type: 'layout-shift', buffered: true })
    })

    await page.goto(`${PAGE}${PAGE.includes('?') ? '&' : '?'}cb=${Date.now()}`, { waitUntil: 'networkidle', timeout: 60000 })
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 450) {
        window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 90))
      }
    })
    // ΚΡΙΣΙΜΟ: οι lazy εικόνες δεν έχουν φορτώσει όταν σταματά το scroll.
    // Χωρίς decode() το test βγάζει ψεύτικες «σπασμένες εικόνες».
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => null))))

    const m = await page.evaluate(() => ({
      cls: Math.round((window.__cls || 0) * 1000) / 1000,
      overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      broken: [...document.images].filter((i) => i.naturalWidth === 0).map((i) => i.getAttribute('src')),
      unsized: [...document.images].filter((i) => !i.getAttribute('width') || !i.getAttribute('height')).length,
      images: document.images.length,
      // Κενά iframes: το site ενός πελάτη έστελνε X-Frame-Options και το πλαίσιο
      // έμενε λευκό, ενώ το κείμενο υποσχόταν «αυτό που βλέπεις είναι ζωντανό».
      iframes: [...document.querySelectorAll('iframe')].map((f) => f.src).filter(Boolean),
    }))

    check(!m.overflow, 'χωρίς οριζόντιο overflow')
    check(m.broken.length === 0, `${m.images} εικόνες, καμία σπασμένη`, m.broken.join(', '))
    check(m.unsized === 0, 'όλες οι εικόνες με width/height', m.unsized ? `${m.unsized} χωρίς` : '')
    check(m.cls < 0.1, `CLS ${m.cls}`)
    check(errors.length === 0, 'χωρίς console errors', errors.join(' | '))
    check(failed.length === 0, 'χωρίς 4xx/5xx', failed.join(' | '))
    if (m.iframes.length) {
      check(false, 'iframes τρίτων στη σελίδα', `${m.iframes.join(', ')} — έλεγξε X-Frame-Options`)
    }
    await ctx.close()
  }
}

async function interaction(browser) {
  head('[αλληλεπίδραση]')
  let ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
  let page = await ctx.newPage()
  await page.goto(PAGE, { waitUntil: 'networkidle', timeout: 60000 })
  const hasShowcase = await page.$('.show-card')
  if (hasShowcase) {
    await page.evaluate(() => document.querySelector('.show-grid').scrollIntoView({ block: 'center' }))
    await page.waitForTimeout(600)
    await page.hover('.show-card')
    await page.waitForTimeout(2900)
    const hover = await page.evaluate(() =>
      new DOMMatrix(getComputedStyle(document.querySelector('.show-card .show-desk')).transform).m42)
    check(hover < -150, 'hover κυλάει την προεπισκόπηση', `${Math.round(hover)}px`)

    await page.evaluate(() => document.querySelectorAll('.show-card')[2].focus())
    await page.waitForTimeout(2900)
    const focus = await page.evaluate(() =>
      new DOMMatrix(getComputedStyle(document.querySelectorAll('.show-card')[2].querySelector('.show-desk')).transform).m42)
    check(focus < -150, 'το ίδιο με πληκτρολόγιο (focus)', `${Math.round(focus)}px`)
  }
  await ctx.close()

  ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' })
  page = await ctx.newPage()
  await page.goto(PAGE, { waitUntil: 'networkidle', timeout: 60000 })
  if (hasShowcase) {
    await page.evaluate(() => document.querySelector('.show-grid').scrollIntoView({ block: 'center' }))
    await page.waitForTimeout(500)
    await page.hover('.show-card')
    await page.waitForTimeout(1500)
    const still = await page.evaluate(() =>
      new DOMMatrix(getComputedStyle(document.querySelector('.show-card .show-desk')).transform).m42)
    check(Math.abs(still) < 1, 'prefers-reduced-motion το ακυρώνει', `${Math.round(still)}px`)
  }
  await ctx.close()
}

async function flow(browser) {
  head('[ροή prompt → δημιουργία]')
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
  const page = await ctx.newPage()

  // Το POST /start κόβεται ΕΠΙΤΗΔΕΣ: αλλιώς κάθε εκτέλεση του QA δημιουργεί
  // αληθινό πελάτη στη βάση παραγωγής. Ελέγχουμε ότι το αίτημα φεύγει με το
  // σωστό σώμα — αυτό αποδεικνύει τη σύνδεση χωρίς να γράψει τίποτα.
  let sent = null
  await page.route('**/start', (route) => {
    if (route.request().method() === 'POST') {
      try { sent = JSON.parse(route.request().postData() || '{}') } catch { sent = {} }
      return route.abort()
    }
    return route.continue()
  })

  await page.goto(PAGE, { waitUntil: 'networkidle', timeout: 60000 })
  await page.fill('#prompt', 'Έχω καφετέρια στον Γέρακα')
  await Promise.all([page.waitForNavigation({ timeout: 20000 }), page.click('.build')])

  // Το Cloudflare Pages σερβίρει το start.html ως /start — δέχονται και τα δύο.
  check(/\/start(\.html)?\?text=/.test(page.url()), 'το prompt πάει στη δημιουργία',
        decodeURIComponent(page.url()).split('/').pop().slice(0, 46))

  await page.waitForTimeout(2500)
  check(sent?.text?.includes('καφετέρια'), 'η οθόνη καλεί το POST /start',
        sent ? JSON.stringify(sent).slice(0, 46) : 'δεν στάλθηκε')
  check(await page.$('#stages li') !== null, 'εμφανίζονται τα στάδια εργασίας')
  await ctx.close()
}

async function demoLinks() {
  head('[demo links]')
  for (const d of DEMOS) {
    let status = 0
    try { status = (await fetch(`${SITES}/preview/${d}`)).status } catch { /* κάτω */ }
    check(status === 200, d, String(status))
  }
}

// ───────────────────────────────────────────────────────── Lighthouse
async function audit() {
  const lighthouse = (await import('lighthouse')).default
  const browser = await chromium.launch({ args: ['--remote-debugging-port=9222'] })
  try {
    for (const form of ['mobile', 'desktop']) {
      head(`[Lighthouse — ${form}]`)
      const opts = { port: 9222, output: 'json', logLevel: 'error', formFactor: form }
      if (form === 'desktop') {
        opts.screenEmulation = { mobile: false, width: 1350, height: 940, deviceScaleFactor: 1, disabled: false }
        opts.throttling = { rttMs: 40, throughputKbps: 10240, cpuSlowdownMultiplier: 1 }
      }
      const { lhr } = await lighthouse(PAGE, opts)

      for (const [key, min] of Object.entries(LH[form])) {
        const score = Math.round(lhr.categories[key].score * 100)
        // Το performance κυμαίνεται με το δίκτυο· τα υπόλοιπα είναι ντετερμινιστικά.
        check(score >= min, `${key} ${score}`, `όριο ${min}`,
              key === 'performance' ? 'perf' : 'critical')
      }
      for (const [key, max] of Object.entries(VITALS[form])) {
        const a = lhr.audits[key]
        if (!a || a.numericValue == null) continue
        // Το CLS είναι σφάλμα διάταξης, όχι διακύμανση δικτύου — κρίσιμο.
        check(a.numericValue <= max, `${key} ${a.displayValue}`,
              `όριο ${key.includes('shift') ? max : max + 'ms'}`,
              key === 'cumulative-layout-shift' ? 'critical' : 'perf')
      }
      // Χωρίς όριο — πολύ θορυβώδες σε lab, αλλά χρήσιμο να το βλέπουμε.
      const si = lhr.audits['speed-index']
      if (si) console.log(`    · speed-index ${si.displayValue} (χωρίς όριο, θορυβώδες)`)

      // Ποια accessibility audits έπεσαν — για να μη μαντεύουμε.
      for (const ref of lhr.categories.accessibility.auditRefs) {
        const a = lhr.audits[ref.id]
        if (a.score !== null && a.score < 1) {
          console.log(`    ! a11y: ${a.id} — ${(a.details?.items || []).length || ''} στοιχεία`)
        }
      }
    }
  } finally {
    await browser.close()
  }
}

// ───────────────────────────────────────────────────────────────────
const main = async () => {
  console.log('='.repeat(64))
  console.log(`VITRINA — production QA\n${PAGE}`)
  console.log('='.repeat(64))

  const browser = await chromium.launch()
  try {
    await behaviour(browser)
    await interaction(browser)
    await flow(browser)
  } finally {
    await browser.close()
  }
  await demoLinks()
  if (!SKIP_LH) await audit()
  else console.log('\n[Lighthouse] παραλείφθηκε (--skip-lighthouse)')

  console.log(`\n${'='.repeat(64)}`)
  console.log(`ΠΕΡΑΣΑΝ: ${pass.length}   ΚΡΙΣΙΜΑ: ${failCritical.length}   ΕΠΙΔΟΣΕΙΣ: ${failPerf.length}`)

  if (failCritical.length) {
    console.log('\n❌ ΤΟ DEPLOY ΘΕΩΡΕΙΤΑΙ ΑΠΟΤΥΧΗΜΕΝΟ — κρίσιμες αποτυχίες:')
    console.log('   • ' + failCritical.join('\n   • '))
    if (failPerf.length) console.log('\n   (επίσης κάτω από όριο: ' + failPerf.join(', ') + ')')
    return 1
  }
  if (failPerf.length) {
    console.log('\n⚠️  Κρίσιμα καθαρά, αλλά επιδόσεις κάτω από το όριο:')
    console.log('   • ' + failPerf.join('\n   • '))
    console.log('\n   Τα σκορ κυμαίνονται μεταξύ εκτελέσεων. Ξανατρέξε πριν επέμβεις·')
    console.log('   αν επιμένει, είναι πραγματική οπισθοδρόμηση.')
    return 2
  }
  console.log('\n✅ Καθαρό — μπορεί να δοθεί link.')
  return 0
}

main().then((c) => process.exit(c)).catch((e) => {
  console.error(`\n✗ ${e.message}`)
  process.exit(1)
})
