#!/usr/bin/env node
/**
 * Release-candidate browser QA: τι βλέπει ο πελάτης, σε τρία πλάτη.
 *
 * ΔΕΝ κρίνει αισθητική και ΔΕΝ αγγίζει themes/ranking. Μετράει τέσσερα
 * πράγματα που ή ισχύουν ή δεν ισχύουν:
 *
 *   1. οριζόντια υπερχείλιση      — η σελίδα κουνιέται πλάγια
 *   2. σπασμένες εικόνες          — μετά από `img.decode()`, όχι πριν
 *   3. ενότητες που λείπουν       — hero, επικοινωνία, CTA
 *   4. κρυμμένο/κομμένο περιεχόμενο — στοιχεία εκτός viewport ή μηδενικά
 *
 * Ο κανόνας του CLAUDE.md: κάθε vertical δοκιμάζεται με τα ΔΙΚΑ ΤΟΥ demo
 * δεδομένα (`?biz=<key>`). Ιατρικό theme με φωτογραφίες ξυλουργού έκρυβε
 * πραγματικά σφάλματα πίσω από τον θόρυβο της αναντιστοιχίας.
 *
 *   node sites/tests/rcBrowserQa.mjs --base http://localhost:3810
 */
import fs from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'

const args = process.argv.slice(2)
const at = (n, d) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] ? args[i + 1] : d }
const BASE = at('--base', 'http://localhost:3810')
const OUT = path.resolve(at('--out', 'artifacts/rc-browser-qa'))

// Ένα demo business ανά οικογένεια σχεδίασης — όχι και τα 18, αλλά αρκετά
// ώστε να πιαστεί υπερχείλιση ή σπασμένη εικόνα που αφορά δομή, όχι θέμα.
const CASES = [
  { biz: 'taverna',   tpl: 'warmth',         label: 'ταβέρνα' },
  { biz: 'dentist',   tpl: 'clinic-triage',  label: 'οδοντιατρείο' },
  { biz: 'carpenter', tpl: 'canvas',         label: 'ξυλουργός' },
  { biz: 'nails',     tpl: 'beauty-atelier', label: 'νυχάδικο' },
  { biz: 'plumber',   tpl: 'callout',        label: 'υδραυλικός' },
  { biz: 'rooms',     tpl: 'aegean',         label: 'ενοικιαζόμενα' },
]
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 1024 },
  { name: 'mobile390', width: 390, height: 844 },
  { name: 'mobile320', width: 320, height: 640 },
]

const results = []
const fail = (viewport, biz, kind, detail) =>
  results.push({ ok: false, viewport, biz, kind, detail })
const pass = (viewport, biz, kind) =>
  results.push({ ok: true, viewport, biz, kind })

async function audit(page, vp, biz) {
  // ΕΙΚΟΝΕΣ — ΔΥΟ ΛΑΘΗ ΜΕΤΡΗΣΗΣ ΠΟΥ ΕΓΙΝΑΝ ΕΔΩ ΚΑΙ ΔΙΟΡΘΩΘΗΚΑΝ:
  //
  // 1. Χωρίς scroll, οι lazy εικόνες δεν ξεκινούν καν να φορτώνουν και
  //    φαίνονται «σπασμένες».
  // 2. Με όριο 4s στο `decode()`, έξι ταυτόχρονες εικόνες σε στενό viewport
  //    χάνουν την προθεσμία και αναφέρονται λανθασμένα ως σπασμένες.
  //
  // Μετρήθηκε: και οι έξι «σπασμένες» σέρβιραν κανονικά — 200 με 82KB/106KB
  // τοπικά και 180ms από το Unsplash. Ήταν αποτυχία του μετρητή, όχι του
  // προϊόντος. Τώρα: κυλάμε πρώτα ΟΛΗ τη σελίδα, μετά κρίνουμε.
  await page.evaluate(async () => {
    const step = Math.round(window.innerHeight * 0.8)
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      window.scrollTo(0, y)
      await new Promise(r => setTimeout(r, 120))
    }
    window.scrollTo(0, 0)
    await new Promise(r => setTimeout(r, 200))
  })
  const images = await page.evaluate(async () => {
    const out = []
    for (const img of document.querySelectorAll('img')) {
      try { await Promise.race([img.decode(), new Promise((_, r) => setTimeout(r, 15000))]) }
      catch { /* το naturalWidth από κάτω είναι η πραγματική ετυμηγορία */ }
      out.push({
        src: (img.currentSrc || img.src || '').slice(0, 120),
        alt: img.getAttribute('alt'),
        broken: img.naturalWidth === 0,
        hidden: img.offsetParent === null && getComputedStyle(img).position !== 'fixed',
      })
    }
    return out
  })
  const broken = images.filter(i => i.broken && !i.hidden)
  broken.length ? fail(vp.name, biz, 'σπασμένες εικόνες',
                       broken.map(b => b.src).join(' | ').slice(0, 200))
                : pass(vp.name, biz, 'εικόνες')

  const noAlt = images.filter(i => i.alt === null)
  noAlt.length ? fail(vp.name, biz, 'εικόνα χωρίς alt',
                      `${noAlt.length} από ${images.length}`)
               : pass(vp.name, biz, 'alt σε κάθε εικόνα')

  // ΥΠΕΡΧΕΙΛΙΣΗ: το σώμα δεν επιτρέπεται να κυλά πλάγια. Καταγράφουμε ΚΑΙ
  // ποιο στοιχείο φταίει — αλλιώς το εύρημα δεν διορθώνεται.
  const overflow = await page.evaluate((w) => {
    const doc = document.documentElement
    const scroll = Math.max(doc.scrollWidth, document.body.scrollWidth)
    if (scroll <= w + 1) return null
    const guilty = []
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect()
      if (r.width === 0 || getComputedStyle(el).position === 'fixed') continue
      if (r.right > w + 1) {
        guilty.push(`${el.tagName.toLowerCase()}.${(el.className || '').toString().split(' ')[0]} → ${Math.round(r.right)}px`)
        if (guilty.length >= 4) break
      }
    }
    return { scroll, guilty }
  }, vp.width)
  overflow ? fail(vp.name, biz, 'οριζόντια υπερχείλιση',
                  `${overflow.scroll}px > ${vp.width}px · ${overflow.guilty.join(' · ')}`)
           : pass(vp.name, biz, 'χωρίς οριζόντια υπερχείλιση')

  // ΕΝΟΤΗΤΕΣ: ένα site χωρίς τρόπο επικοινωνίας δεν είναι site.
  const structure = await page.evaluate(() => ({
    h1: document.querySelectorAll('h1').length,
    tel: document.querySelectorAll('a[href^="tel:"]').length,
    sections: document.querySelectorAll('section').length,
    textLength: (document.body.innerText || '').trim().length,
  }))
  structure.h1 === 1 ? pass(vp.name, biz, 'ακριβώς ένα h1')
                     : fail(vp.name, biz, 'h1', `βρέθηκαν ${structure.h1}`)
  structure.tel >= 1 ? pass(vp.name, biz, 'σύνδεσμος κλήσης')
                     : fail(vp.name, biz, 'λείπει tel: link', 'καμία ενέργεια κλήσης')
  structure.sections >= 3 ? pass(vp.name, biz, 'ενότητες περιεχομένου')
                          : fail(vp.name, biz, 'λίγες ενότητες', `${structure.sections}`)
  structure.textLength > 400 ? pass(vp.name, biz, 'υπάρχει περιεχόμενο')
                             : fail(vp.name, biz, 'σχεδόν άδεια σελίδα',
                                    `${structure.textLength} χαρακτήρες`)

  // ΚΟΜΜΕΝΟ ΠΕΡΙΕΧΟΜΕΝΟ: κείμενο που ξεχειλίζει από το κουτί του.
  const clipped = await page.evaluate(() => {
    const bad = []
    for (const el of document.querySelectorAll('h1,h2,h3,p,button,a,li')) {
      const s = getComputedStyle(el)
      if (s.overflow === 'visible' || el.offsetWidth === 0) continue
      if (el.scrollWidth > el.clientWidth + 2 && s.textOverflow !== 'ellipsis') {
        bad.push(`${el.tagName.toLowerCase()}: ${(el.innerText || '').slice(0, 40)}`)
        if (bad.length >= 3) break
      }
    }
    return bad
  })
  clipped.length ? fail(vp.name, biz, 'κομμένο κείμενο', clipped.join(' · '))
                 : pass(vp.name, biz, 'κανένα κομμένο κείμενο')
}

const run = async () => {
  await fs.mkdir(OUT, { recursive: true })
  const browser = await chromium.launch()
  const consoleErrors = []
  for (const vp of VIEWPORTS) {
    const ctx = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1, locale: 'el-GR',
      reducedMotion: 'reduce',   // σταθερά screenshots· δεν κρίνουμε κίνηση εδώ
    })
    const page = await ctx.newPage()
    page.on('console', m => { if (m.type() === 'error') consoleErrors.push(`${vp.name}: ${m.text().slice(0, 140)}`) })
    page.on('pageerror', e => consoleErrors.push(`${vp.name}: ${String(e).slice(0, 140)}`))
    for (const c of CASES) {
      const url = `${BASE}/preview/${c.tpl}?biz=${c.biz}`
      try {
        const r = await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 })
        if (!r || !r.ok()) { fail(vp.name, c.biz, 'δεν φόρτωσε', `HTTP ${r && r.status()}`); continue }
        await page.waitForTimeout(400)
        await audit(page, vp, c.biz)
        await page.screenshot({
          path: path.join(OUT, `${c.biz}-${vp.name}.jpg`),
          fullPage: true, type: 'jpeg', quality: 72,
        })
      } catch (e) {
        fail(vp.name, c.biz, 'εξαίρεση', String(e).slice(0, 160))
      }
    }
    await ctx.close()
  }
  await browser.close()

  const failed = results.filter(r => !r.ok)
  const byKind = {}
  for (const f of failed) (byKind[f.kind] ||= []).push(`${f.biz}/${f.viewport}: ${f.detail}`)
  console.log(`\nΈλεγχοι: ${results.length}   ΠΕΡΑΣΑΝ: ${results.length - failed.length}   ΕΣΠΑΣΑΝ: ${failed.length}`)
  for (const [kind, items] of Object.entries(byKind)) {
    console.log(`\n  ✗ ${kind}  (${items.length})`)
    items.slice(0, 6).forEach(i => console.log(`      · ${i}`))
  }
  if (consoleErrors.length) {
    console.log(`\n  ⚠ console errors: ${consoleErrors.length}`)
    ;[...new Set(consoleErrors)].slice(0, 5).forEach(e => console.log(`      · ${e}`))
  }
  await fs.writeFile(path.join(OUT, 'results.json'),
                     JSON.stringify({ results, consoleErrors }, null, 2))
  console.log(`\n  screenshots: ${OUT}`)
  process.exit(failed.length ? 1 : 0)
}
run()
