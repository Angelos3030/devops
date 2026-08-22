import { chromium } from 'playwright'
import fs from 'fs'

// QA κάθε theme στην ΠΑΡΑΓΩΓΗ, με το demo business του δικού του vertical (CLAUDE.md §7β).
const BASE = 'https://sites-production-da56.up.railway.app/preview/'
const OUT = 'c:/greek-smb-agent/research/theme-library/'
const reg = JSON.parse(fs.readFileSync(OUT + 'registry.json', 'utf8'))

// backend vertical -> demo business key του sites/lib/demoData.js
const BIZ = {
  food: 'taverna', bakery: 'cafe', cafe: 'cafe', beauty: 'salon', aesthetics: 'aesthetics',
  dentist: 'dentist', doctor: 'physician', pharmacy: 'pharmacy', massage: 'massage',
  gym: 'gym', rooms: 'rooms', realestate: 'realestate', retail: 'retail',
  trade: 'plumber', wood: 'carpenter', garage: 'garage', farm: 'farm',
  professional: 'lawyer', pet: 'retail',
}
// Τα 15 που δεν υπάρχουν σε κανένα vertical του backend. Το vertical προκύπτει
// από το ίδιο το όνομα/ταυτότητα του theme — ΟΧΙ αυθαίρετα, και ποτέ 'plumber'
// για ένα theme καφέ (CLAUDE.md §7β).
const OVERRIDE = {
  'klassy-cafe': 'cafe', 'frost-bakery': 'bakery', 'moso-interior': 'wood',
  'barber-shop': 'beauty', 'billys-barber': 'beauty', 'thomson-stylist': 'beauty',
  'gymso-fitness': 'gym', 'pulse': 'gym', 'medic-care': 'doctor',
  'villa-agency': 'realestate', 'coast': 'rooms', 'clean-work': 'trade',
  'blue-onepage': 'professional', 'corporate': 'professional', 'showcase': 'retail',
}
const themeVertical = { ...OVERRIDE }
for (const [v, keys] of Object.entries(reg.by_vertical)) {
  for (const k of keys) if (!themeVertical[k]) themeVertical[k] = v   // το override έχει προτεραιότητα
}

const ids = reg.render_ids
const only = process.argv[2] ? process.argv[2].split(',') : null
const list = only ? ids.filter(i => only.includes(i)) : ids
console.log('themes προς έλεγχο:', list.length)

const b = await chromium.launch()
const results = []
let n = 0

for (const id of list) {
  n++
  const vert = themeVertical[id] || 'trade'
  const biz = BIZ[vert] || 'plumber'
  const url = `${BASE}${id}?biz=${biz}`
  const r = { id, vertical: vert, biz, url, checks: {} }

  for (const [tag, w, h] of [['desktop', 1440, 900], ['mobile', 390, 844]]) {
    const p = await b.newPage({ viewport: { width: w, height: h }, locale: 'el-GR' })
    const errs = [], failed = []
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 110)) })
    p.on('requestfailed', q => failed.push(q.url().slice(-60)))
    try {
      const resp = await p.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 })
      r.status = resp.status()
      await p.waitForTimeout(1400)
      // lazy εικόνες: εξαναγκασμός φόρτωσης ΠΡΙΝ το decode
      await p.evaluate(async () => {
        const a = [...document.querySelectorAll('img')].filter(i => i.getAttribute('src'))
        a.forEach(i => { i.loading = 'eager' })
        await Promise.all(a.map(i => i.complete ? null : new Promise(res => {
          i.addEventListener('load', res, { once: true })
          i.addEventListener('error', res, { once: true })
          setTimeout(res, 6000)
        })))
      })
      await p.waitForTimeout(500)
      const m = await p.evaluate(async () => {
        const g = e => getComputedStyle(e)
        let ok = 0, broken = []
        for (const i of document.querySelectorAll('img')) {
          const src = i.getAttribute('src'); if (!src) continue
          if (i.complete && i.naturalWidth > 0) {
            try { await i.decode(); ok++ } catch (e) { broken.push(src.split('/').pop()) }
          } else broken.push(src.split('/').pop())
        }
        const over = [...document.querySelectorAll('body *')].filter(e => {
          const q = e.getBoundingClientRect()
          if (!q.width) return false
          let a = e.parentElement
          while (a) { const s = g(a)
            if (/hidden|clip|auto|scroll/.test(s.overflow + s.overflowX)) return false
            a = a.parentElement }
          return q.right > document.documentElement.clientWidth + 2
        }).map(e => e.tagName + '.' + String(e.className).slice(0, 22)).slice(0, 4)
        const localhost = [...document.querySelectorAll('[src],[href]')]
          .map(e => e.getAttribute('src') || e.getAttribute('href') || '')
          .filter(u => /localhost|127\.0\.0\.1|:3000|:3800/.test(u)).slice(0, 3)
        return {
          docW: document.documentElement.scrollWidth,
          clientW: document.documentElement.clientWidth,
          docH: document.documentElement.scrollHeight,
          imgsOk: ok, imgsBroken: broken.slice(0, 4), imgCount: document.querySelectorAll('img').length,
          h1: document.querySelectorAll('h1').length,
          textLen: document.body.innerText.trim().length,
          over, localhost,
          hasNav: !!document.querySelector('nav,header'),
          tel: document.querySelectorAll('a[href^="tel:"]').length,
        }
      })
      r.checks[tag] = { ...m, consoleErrors: errs.slice(0, 3), failedRequests: failed.slice(0, 3) }
      if (tag === 'desktop') {
        await p.screenshot({ path: `${OUT}shots/${id}.jpg`, type: 'jpeg', quality: 55,
          clip: { x: 0, y: 0, width: w, height: h } })
      }
    } catch (e) {
      r.checks[tag] = { error: String(e).slice(0, 90) }
    }
    await p.close()
  }

  // κρίση
  const d = r.checks.desktop || {}, mo = r.checks.mobile || {}
  const fail = []
  if (r.status !== 200) fail.push('HTTP ' + r.status)
  if (d.error || mo.error) fail.push('σφάλμα φόρτωσης')
  if (d.docW > d.clientW + 2) fail.push('οριζόντια υπερχείλιση desktop')
  if (mo.docW > mo.clientW + 2) fail.push('οριζόντια υπερχείλιση mobile')
  if ((d.imgsBroken || []).length) fail.push('σπασμένες εικόνες ' + d.imgsBroken.length)
  if ((d.localhost || []).length) fail.push('localhost reference')
  if ((d.consoleErrors || []).length) fail.push('console error')
  if (d.h1 !== 1) fail.push('h1 ×' + d.h1)
  if ((d.textLen || 0) < 400) fail.push('σχεδόν κενό (' + d.textLen + ' χαρ.)')
  r.fail = fail
  r.pass = fail.length === 0
  results.push(r)
  console.log(`${String(n).padStart(2)}/${list.length} ${r.pass ? '✓' : '✗'} ${id.padEnd(22)} ${biz.padEnd(11)} ${fail.join(', ')}`)
  fs.writeFileSync(OUT + 'qa.json', JSON.stringify(results, null, 1))
}

const pass = results.filter(r => r.pass).length
console.log(`\nΠΕΡΑΣΑΝ ${pass}/${results.length} · ΑΠΕΤΥΧΑΝ ${results.length - pass}`)
await b.close()
