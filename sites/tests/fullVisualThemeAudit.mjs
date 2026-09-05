import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'
import { execFileSync } from 'node:child_process'

const base = process.env.QA_BASE || 'http://127.0.0.1:3900'
const phase = process.env.QA_PHASE || 'before'
const requestedIds = new Set((process.env.QA_THEME_IDS || '').split(',').map((id) => id.trim()).filter(Boolean))
const forceNarrow = process.env.QA_FORCE_NARROW === '1'
const root = path.resolve(process.cwd(), '..')
const out = path.join(root, 'research', 'visual-theme-audit', phase)
const shots = path.join(out, 'screenshots')
fs.mkdirSync(shots, { recursive: true })
if (phase === 'before') {
  fs.writeFileSync(path.join(root, 'research', 'visual-theme-audit', 'worktree-start.txt'),
    execFileSync('git', ['status', '--short'], { cwd: root, encoding: 'utf8' }))
}

const source = fs.readFileSync(path.join(process.cwd(), 'lib', 'templates', 'index.js'), 'utf8')
const commercialIds = [...source.match(/export const COMMERCIAL_THEMES = \[(.*?)\]/s)[1].matchAll(/"([^"]+)"/g)].map((m) => m[1])
if (commercialIds.length !== 58) throw new Error(`expected 58 commercial themes, found ${commercialIds.length}`)
const ids = requestedIds.size ? commercialIds.filter((id) => requestedIds.has(id)) : commercialIds
if (requestedIds.size && ids.length !== requestedIds.size) {
  const missing = [...requestedIds].filter((id) => !commercialIds.includes(id))
  throw new Error(`unknown requested theme ids: ${missing.join(', ')}`)
}

const primary = new Map()
for (const id of ids) {
  const marker = `${id.includes('-') ? `'${id}'` : id}: {`
  const start = source.indexOf(marker, source.indexOf('export const TEMPLATE_META'))
  const body = source.slice(start, start + 900)
  primary.set(id, body.match(/primary:\s*'([^']+)'/)?.[1] || 'trade')
}

const BIZ = {
  food: 'taverna', bakery: 'cafe', cafe: 'cafe', beauty: 'salon',
  aesthetics: 'aesthetics', dentist: 'dentist', doctor: 'physician',
  pharmacy: 'pharmacy', massage: 'massage', gym: 'gym', rooms: 'rooms',
  realestate: 'realestate', retail: 'retail', trade: 'plumber', wood: 'carpenter',
  garage: 'garage', farm: 'farm', professional: 'lawyer', pet: 'retail',
  education: 'education', logistics: 'logistics',
}

const browser = await chromium.launch({ headless: true })
const results = []
const measurementsFile = path.join(out, 'measurements.json')

async function settleVisuals(page) {
  await page.evaluate(async () => {
    const settle = Promise.all([
      document.fonts.ready.catch(() => null),
      ...[...document.images].map((img) => img.decode().catch(() => null)),
    ])
    await Promise.race([settle, new Promise((resolve) => setTimeout(resolve, 8_000))])
  })
  await page.evaluate(async () => {
    const step = Math.max(320, Math.floor(innerHeight * 0.72))
    const maxY = Math.max(0, document.documentElement.scrollHeight - innerHeight)
    for (let y = 0; y <= maxY; y += step) {
      scrollTo(0, y)
      await new Promise((resolve) => setTimeout(resolve, 90))
    }
    scrollTo(0, maxY)
    await new Promise((resolve) => setTimeout(resolve, 180))
    scrollTo(0, 0)
    await new Promise((resolve) => setTimeout(resolve, 180))
  })
}

function persist() {
  fs.writeFileSync(measurementsFile, JSON.stringify({ phase, base, themes: results }, null, 2))
}

for (const [index, id] of ids.entries()) {
  const vertical = primary.get(id)
  const biz = BIZ[vertical] || 'plumber'
  const result = { id, vertical, biz, url: `${base}/preview/${id}?biz=${biz}`, viewports: {} }
  for (const [label, width, height] of [['desktop', 1440, 1024], ['mobile', 390, 844]]) {
    const page = await browser.newPage({
      viewport: { width, height },
      deviceScaleFactor: 1,
      reducedMotion: 'reduce',
    })
    const consoleErrors = []
    const pageErrors = []
    const requestFailures = []
    page.on('console', (msg) => { if (msg.type() === 'error') consoleErrors.push(msg.text()) })
    page.on('pageerror', (err) => pageErrors.push(err.message))
    page.on('requestfailed', (req) => requestFailures.push(`${req.url()} :: ${req.failure()?.errorText || ''}`))
    const response = await page.goto(result.url, { waitUntil: 'networkidle', timeout: 45_000 })
    await settleVisuals(page)
    const metrics = await page.evaluate(() => {
      const rect = (el) => {
        const r = el.getBoundingClientRect()
        return { x: r.x, y: r.y, width: r.width, height: r.height, right: r.right, bottom: r.bottom }
      }
      const visible = (el) => {
        const r = el.getBoundingClientRect()
        const s = getComputedStyle(el)
        return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) !== 0
      }
      const headings = [...document.querySelectorAll('h1,h2,h3')].filter(visible).map((el) => {
        const r = rect(el); const s = getComputedStyle(el)
        return {
          tag: el.tagName, text: el.textContent.trim().slice(0, 180), ...r,
          fontSize: parseFloat(s.fontSize), lineHeight: s.lineHeight,
          clipped: el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + 2,
          outside: r.x < -2 || r.right > innerWidth + 2,
        }
      })
      const images = [...document.images].filter(visible).map((el) => ({
        src: el.currentSrc || el.src, alt: el.alt, naturalWidth: el.naturalWidth,
        naturalHeight: el.naturalHeight, objectFit: getComputedStyle(el).objectFit,
        objectPosition: getComputedStyle(el).objectPosition, ...rect(el),
      }))
      const sections = [...document.querySelectorAll('main > section, body > section, main > div')].filter(visible).map((el) => {
        const r = rect(el)
        const children = [...el.children].filter(visible).map(rect)
        const contentHeight = children.length ? Math.max(...children.map((x) => x.bottom)) - Math.min(...children.map((x) => x.y)) : 0
        return { role: el.tagName, className: String(el.className).slice(0, 100), ...r, contentHeight,
          emptyRatio: r.height > 0 ? Math.max(0, 1 - contentHeight / r.height) : 0 }
      })
      const interactives = [...document.querySelectorAll('a,button,input,select,textarea')].filter(visible).map((el) => ({
        label: (el.textContent || el.getAttribute('aria-label') || '').trim().slice(0, 80), ...rect(el),
      }))
      const textNodes = [...document.querySelectorAll('h1,h2,h3,p,a,button,li')].filter(visible)
      const overlaps = []
      for (let i = 0; i < textNodes.length; i++) for (let j = i + 1; j < textNodes.length; j++) {
        const a = textNodes[i].getBoundingClientRect(), b = textNodes[j].getBoundingClientRect()
        const area = Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top))
        if (area > 80 && !textNodes[i].contains(textNodes[j]) && !textNodes[j].contains(textNodes[i])) overlaps.push({
          a: textNodes[i].textContent.trim().slice(0, 70), b: textNodes[j].textContent.trim().slice(0, 70), area: Math.round(area),
        })
      }
      return {
        title: document.title, h1Count: document.querySelectorAll('h1').length,
        bodyHeight: document.documentElement.scrollHeight,
        horizontalOverflow: document.documentElement.scrollWidth - innerWidth,
        headings, images, sections, interactives,
        overlaps: overlaps.slice(0, 30),
      }
    })
    const suspicious = metrics.horizontalOverflow > 2 || metrics.images.some((img) => !img.naturalWidth) ||
      metrics.headings.some((h) => h.clipped || h.outside || h.fontSize > Math.max(110, width * 0.12) || h.height > height * 0.72) ||
      metrics.overlaps.length > 0 || metrics.sections.some((s) => s.height > height * 1.4 && s.emptyRatio > 0.6)
    const file = path.join(shots, `${id}-${label}.png`)
    await page.screenshot({ path: file, fullPage: true, animations: 'disabled' })
    result.viewports[label] = { status: response?.status() || 0, screenshot: path.relative(root, file).replaceAll('\\', '/'),
      consoleErrors, pageErrors, requestFailures, suspicious, ...metrics }
    await page.close()
  }
  if (forceNarrow || result.viewports.desktop.suspicious || result.viewports.mobile.suspicious) {
    const page = await browser.newPage({
      viewport: { width: 320, height: 720 },
      deviceScaleFactor: 1,
      reducedMotion: 'reduce',
    })
    await page.goto(result.url, { waitUntil: 'networkidle', timeout: 45_000 })
    await settleVisuals(page)
    const file = path.join(shots, `${id}-narrow.png`)
    await page.screenshot({ path: file, fullPage: true, animations: 'disabled' })
    result.viewports.narrow = { screenshot: path.relative(root, file).replaceAll('\\', '/') }
    await page.close()
  }
  results.push(result)
  persist()
  console.log(`[${String(index + 1).padStart(2, '0')}/${ids.length}] ${id} (${vertical}/${biz})`)
}

await browser.close()
persist()
console.log(`fullVisualThemeAudit: ${results.length} themes complete -> ${out}`)
