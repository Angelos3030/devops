import { chromium } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const base = process.env.SITES_BASE_URL || 'http://127.0.0.1:3000'
const templates = [
  'editorial', 'split', 'showcase', 'bento', 'longform', 'corporate',
  'poster', 'sidebar', 'grid', 'coast', 'magazine', 'warmth', 'ember',
  'marble', 'runway', 'forge', 'aegean', 'bloom', 'pulse', 'volt',
  'motor', 'terra', 'dispatch', 'canvas',
]
const viewports = {
  desktop: { width: 1440, height: 1024 },
  mobile: { width: 390, height: 844 },
}
const official = new Set(['editorial', 'split', 'bento', 'longform', 'poster', 'sidebar', 'grid', 'magazine', 'warmth', 'ember', 'marble', 'runway', 'forge', 'aegean', 'bloom', 'volt', 'motor', 'terra', 'dispatch', 'canvas'])
const outDir = path.resolve('artifacts/template-audit')
await mkdir(outDir, { recursive: true })

const browser = await chromium.launch({ headless: true })
const results = []
for (const template of templates) {
  const cases = [
    ...Object.entries(viewports).map(([viewport, size]) => ({ viewport, size, photoMode: 'real' })),
    ...(official.has(template) ? [{ viewport: 'mobile', size: viewports.mobile, photoMode: 'none' }] : []),
  ]
  for (const { viewport, size, photoMode } of cases) {
    const page = await browser.newPage({ viewport: size })
    const errors = []
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()) })
    page.on('pageerror', error => errors.push(error.message))
    const response = await page.goto(`${base}/preview/${template}?biz=carpenter&photos=${photoMode}`, { waitUntil: 'networkidle' })
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += window.innerHeight * .8) {
        window.scrollTo(0, y)
        await new Promise(resolve => setTimeout(resolve, 80))
      }
      window.scrollTo(0, 0)
    })
    await page.waitForTimeout(250)
    const metrics = await page.evaluate(() => ({
      innerWidth: window.innerWidth,
      scrollWidth: document.documentElement.scrollWidth,
      images: [...document.images].map(img => ({ src: img.currentSrc, width: img.naturalWidth, height: img.naturalHeight })),
    }))
    const shotName = photoMode === 'none' ? `${template}-${viewport}-no-photo.png` : `${template}-${viewport}.png`
    await page.screenshot({ path: path.join(outDir, shotName), fullPage: true })
    results.push({
      template,
      viewport,
      photoMode,
      status: response?.status(),
      overflow: metrics.scrollWidth > metrics.innerWidth,
      brokenImages: metrics.images.filter(img => !img.width || !img.height).length,
      consoleErrors: errors,
    })
    await page.close()
  }
}
await browser.close()
await writeFile(path.join(outDir, 'results.json'), JSON.stringify(results, null, 2))

const failures = results.filter(item => item.status !== 200 || item.overflow || item.brokenImages || item.consoleErrors.length)
console.log(`Audited ${results.length} template/viewports. Issues: ${failures.length}`)
for (const failure of failures) console.log(JSON.stringify(failure))
process.exitCode = failures.length ? 1 : 0
