#!/usr/bin/env node
/**
 * QA για το theme «callout» (τεχνίτες).
 *
 *   node sites/tests/theme_callout_qa.mjs --base http://localhost:3107
 *
 * Πέρα από το design_guard (αντίθεση/fonts/trackers), ελέγχει ό,τι είναι ειδικό
 * σε αυτό το theme: τη φόρμα, το «24/7» που δεν πρέπει να λέει ψέματα, και ότι
 * το τηλέφωνο είναι παντού — γιατί εδώ η μετατροπή είναι η κλήση.
 */
import { chromium } from 'playwright'

const args = process.argv.slice(2)
const i = args.indexOf('--base')
const BASE = i !== -1 && args[i + 1] ? args[i + 1] : 'http://localhost:3107'

const pass = [], fail = []
const check = (ok, label, detail = '') => {
  ;(ok ? pass : fail).push(label)
  console.log(`  ${ok ? '✓' : '✗'} ${label}${detail ? `  — ${detail}` : ''}`)
}

const main = async () => {
  const browser = await chromium.launch()

  for (const [w, h, name] of [[1440, 1024, 'desktop'], [768, 1024, 'tablet'], [390, 844, 'mobile']]) {
    console.log(`\n[${name}]`)
    const ctx = await browser.newContext({
      viewport: { width: w, height: h }, deviceScaleFactor: 1,
      isMobile: w < 500, hasTouch: w < 500,
    })
    const page = await ctx.newPage()
    const errors = []
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text().slice(0, 90)))
    await page.goto(`${BASE}/preview/callout?biz=plumber`, { waitUntil: 'networkidle' })
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += 450) {
        window.scrollTo(0, y); await new Promise((r) => setTimeout(r, 70))
      }
    })
    await page.evaluate(() => Promise.all([...document.images].map((im) => im.decode().catch(() => null))))

    const m = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      broken: [...document.images].filter((im) => im.naturalWidth === 0).length,
      h1: document.querySelectorAll('h1').length,
      tel: document.querySelectorAll('a[href^="tel:"]').length,
      // Tap targets: κάθε ενέργεια πρέπει να πατιέται με αντίχειρα.
      // Το #find-us είναι ΚΟΙΝΟ component — τα δικά του tap targets μετρώνται
      // χωριστά ώστε ένα καθολικό θέμα να μη μπλοκάρει το gate ενός theme.
      small: [...document.querySelectorAll('a, button')].filter((e) => {
        if (e.closest('#find-us')) return false
        const r = e.getBoundingClientRect()
        return r.width > 0 && r.height > 0 && r.height < 44
      }).map((e) => (e.textContent || '').trim().slice(0, 22)),
      sharedSmall: [...document.querySelectorAll('#find-us a, #find-us button')].filter((e) => {
        const r = e.getBoundingClientRect()
        return r.width > 0 && r.height > 0 && r.height < 44
      }).length,
      // Στο κινητό η κάρτα κλήσης πρέπει να έρχεται ΠΡΙΝ το κείμενο.
      quoteFirst: (() => {
        const q = document.querySelector('[class*=quote]')
        const c = document.querySelector('[class*=heroCopy]')
        if (!q || !c) return null
        return q.getBoundingClientRect().top < c.getBoundingClientRect().top
      })(),
    }))

    check(!m.overflow, 'χωρίς οριζόντιο overflow')
    check(m.broken === 0, 'καμία σπασμένη εικόνα')
    check(m.h1 === 1, 'ακριβώς ένα h1', String(m.h1))
    check(m.tel >= 3, `τηλέφωνο σε ${m.tel} σημεία`)
    check(m.small.length === 0, 'tap targets ≥ 44px', m.small.join(', '))
    if (name === 'mobile') {
      check(m.quoteFirst === true, 'στο κινητό η κάρτα κλήσης έρχεται πρώτη')
    }
    if (m.sharedSmall) console.log(`    · (FindUs: ${m.sharedSmall} μικρά tap targets — κοινό component)`)
    check(errors.length === 0, 'χωρίς console errors', errors.join(' | '))
    await ctx.close()
  }

  // ---- Ειλικρίνεια: το «24/7» μόνο όταν ισχύει --------------------------
  console.log('\n[ειλικρίνεια]')
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
  const page = await ctx.newPage()

  await page.goto(`${BASE}/preview/callout?biz=plumber`, { waitUntil: 'networkidle' })
  const plumber = await page.evaluate(() => ({
    body: document.body.innerText,
    hours: document.body.innerText.match(/24\/7[^\n]*/)?.[0] || '',
  }))
  check(/24\/7/.test(plumber.body), 'ο υδραυλικός (ωράριο 24/7) δείχνει 24/7', plumber.hours)
  const badges = await page.evaluate(() =>
    [...document.images].map((im) => `${im.src} ${im.alt}`)
      .filter((t) => /google|yelp|trustpilot|bbb|reviews|certified|πιστοποι/i.test(t)))
  check(badges.length === 0, 'κανένα σήμα κριτικών/πιστοποίησης', badges.join(', '))
  check(!/★★★|4\.9\s*\/\s*5|βαθμολογ/i.test(plumber.body), 'καμία επινοημένη βαθμολογία')

  await page.goto(`${BASE}/preview/callout?biz=salon`, { waitUntil: 'networkidle' })
  const salon = await page.evaluate(() => document.body.innerText)
  check(!/24\/7/.test(salon), 'επιχείρηση με κανονικό ωράριο ΔΕΝ δείχνει 24/7')

  // ---- Φόρμα ------------------------------------------------------------
  console.log('\n[φόρμα]')
  await page.goto(`${BASE}/preview/callout?biz=dentist`, { waitUntil: 'networkidle' })
  const withMail = await page.evaluate(() => ({
    form: Boolean(document.querySelector('form')),
    fields: document.querySelectorAll('form input, form textarea').length,
    required: document.querySelectorAll('form [required]').length,
    labelled: [...document.querySelectorAll('form input, form textarea')]
      .every((el) => el.closest('label') || el.getAttribute('aria-label')),
    telType: Boolean(document.querySelector('form input[type="tel"]')),
  }))
  check(withMail.form, 'με email πελάτη εμφανίζεται φόρμα')
  check(withMail.fields === 3, '3 πεδία', String(withMail.fields))
  check(withMail.required === 2, 'όνομα και τηλέφωνο υποχρεωτικά', String(withMail.required))
  check(withMail.labelled, 'κάθε πεδίο έχει ετικέτα (screen reader)')
  check(withMail.telType, 'το τηλέφωνο ανοίγει αριθμητικό πληκτρολόγιο')

  // Η σύνθεση του mailto ελέγχεται στο editor_rules.mjs (καθαρή συνάρτηση).

  // Χωρίς email: καθόλου φόρμα — αλλιώς θα έστελνε στο πουθενά.
  await page.goto(`${BASE}/preview/callout?biz=plumber`, { waitUntil: 'networkidle' })
  const noMail = await page.evaluate(() => ({
    form: Boolean(document.querySelector('form')),
    call: Boolean(document.querySelector('[class*=quote] a[href^="tel:"]')),
  }))
  check(!noMail.form, 'χωρίς email ΔΕΝ εμφανίζεται φόρμα')
  check(noMail.call, 'στη θέση της, κάρτα κλήσης')

  await ctx.close()
  await browser.close()

  console.log(`\n${'='.repeat(56)}`)
  console.log(`ΠΕΡΑΣΑΝ: ${pass.length}   ΕΣΠΑΣΑΝ: ${fail.length}`)
  if (fail.length) { console.log('\n❌ ' + fail.join('\n   ')); return 1 }
  console.log('\n✅ Το theme τεχνιτών είναι έτοιμο.')
  return 0
}

main().then((c) => process.exit(c)).catch((e) => { console.error(e.message); process.exit(1) })
