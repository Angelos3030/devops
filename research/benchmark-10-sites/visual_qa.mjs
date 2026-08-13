// Phase 3 + 4: μετρήσεις και screenshots από ΠΡΑΓΜΑΤΙΚΟ browser.
// Οι εικόνες κρίνονται ΜΕΤΑ το `img.decode()` και μετά το `document.fonts.ready`
// — αλλιώς φωτογραφίζουμε μια σελίδα που δεν έχει φορτώσει ακόμη.
import { chromium } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'

const BASE = 'http://127.0.0.1:3812/site'
const OUT = 'artifacts/benchmark/shots'
await mkdir(OUT, { recursive: true })

const IDS = ['bench-01-plumber', 'bench-02-electrician', 'bench-03-accountant',
  'bench-04-dietitian', 'bench-05-salon', 'bench-06-bakery', 'bench-07-taverna',
  'bench-08-dentist', 'bench-09-realestate', 'bench-10-petgroomer']

const browser = await chromium.launch()
const results = []

for (const id of IDS) {
  const row = { id, console: [], desktop: null, mobile: null, text: '' }
  for (const [tag, w, h] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' })
    const page = await ctx.newPage()
    page.on('console', (m) => { if (m.type() === 'error') row.console.push(`${tag}: ${m.text().slice(0, 120)}`) })
    page.on('pageerror', (e) => row.console.push(`${tag}: pageerror ${String(e).slice(0, 120)}`))
    const failed = []
    page.on('requestfailed', (r) => failed.push(r.url().slice(0, 80)))
    await page.goto(`${BASE}/${id}`, { waitUntil: 'domcontentloaded', timeout: 45000 })
    await page.evaluate(() => document.fonts.ready)
    await page.evaluate(() => Promise.all([...document.images].map((i) => i.decode().catch(() => null))))
    await page.waitForTimeout(600)
    const m = await page.evaluate(() => {
      const px = (n) => Math.round(n)
      const imgs = [...document.images]
      return {
        height: px(document.body.scrollHeight),
        overflow: px(document.documentElement.scrollWidth - document.documentElement.clientWidth),
        h1: [...document.querySelectorAll('h1')].map((x) => x.textContent.trim()),
        h2count: document.querySelectorAll('h2').length,
        images: imgs.length,
        brokenImages: imgs.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src.slice(0, 70)),
        tinyText: [...document.querySelectorAll('p, li, dd, span')]
          .filter((e) => e.textContent.trim() && parseFloat(getComputedStyle(e).fontSize) < 12).length,
        smallTaps: [...document.querySelectorAll('a[href], button')]
          .filter((a) => { const r = a.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.height < 40 }).length,
        tel: document.querySelectorAll('a[href^="tel:"]').length,
        mailto: document.querySelectorAll('a[href^="mailto:"]').length,
        deadAnchors: [...document.querySelectorAll('a[href^="#"]')]
          .filter((a) => a.getAttribute('href') !== '#' && !document.querySelector(a.getAttribute('href'))).length,
        emptyHref: [...document.querySelectorAll('a')].filter((a) => !a.getAttribute('href')).length,
        text: (document.querySelector('main')?.innerText || document.body.innerText).trim(),
      }
    })
    await page.screenshot({ path: `${OUT}/${id}-${tag}.png`, fullPage: true })
    await ctx.close()
    m.requestFailed = failed.filter((u) => !u.includes('_next')).slice(0, 4)
    if (tag === 'desktop') row.text = m.text
    delete m.text
    row[tag] = m
  }
  results.push(row)
  const d = row.desktop, mo = row.mobile
  console.log(`${id.padEnd(22)} desk ${String(d.height).padStart(5)}px ovf${d.overflow} ` +
    `| mob ${String(mo.height).padStart(5)}px ovf${mo.overflow} | imgs ${d.images}/${d.brokenImages.length}βλ ` +
    `| h1:${d.h1.length} tel:${d.tel} tiny:${d.mobile ?? mo.tinyText} taps<40:${mo.smallTaps} ` +
    `| console:${row.console.length}`)
}

await browser.close()
await writeFile('artifacts/benchmark/qa-metrics.json', JSON.stringify(results, null, 1))
await writeFile('artifacts/benchmark/copy-dump.txt',
  results.map((r) => `\n${'='.repeat(70)}\n${r.id}  —  h1: ${r.desktop.h1.join(' | ')}\n${'='.repeat(70)}\n${r.text}`).join('\n'))
console.log('\nmetrics → artifacts/benchmark/qa-metrics.json · copy → copy-dump.txt')
