import { chromium } from 'playwright'

const base = process.env.QA_BASE || 'http://127.0.0.1:3910'
const cases = [
  ['blue-onepage', 'lawyer'],
  ['educenter-campus', 'education'],
  ['freight-lane', 'logistics'],
]
const viewports = [[1440, 1024], [390, 844], [320, 760]]
const browser = await chromium.launch({ headless: true })
const failures = []

for (const [theme, biz] of cases) {
  for (const [width, height] of viewports) {
    const page = await browser.newPage({ viewport: { width, height }, reducedMotion: 'no-preference' })
    const errors = []
    page.on('console', (msg) => { if (msg.type() === 'error') errors.push(`console: ${msg.text()}`) })
    page.on('pageerror', (error) => errors.push(`page: ${error.message}`))
    const response = await page.goto(`${base}/preview/${theme}?biz=${biz}`, { waitUntil: 'networkidle' })
    await page.evaluate(async () => {
      await document.fonts.ready
      const step = Math.max(240, Math.floor(innerHeight * 0.62))
      for (let y = 0; y <= document.documentElement.scrollHeight - innerHeight; y += step) {
        scrollTo({ top: y, behavior: 'instant' })
        await new Promise((resolve) => setTimeout(resolve, 110))
      }
      scrollTo({ top: 0, behavior: 'instant' })
    })
    const health = await page.evaluate(() => ({
      overflow: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth) - innerWidth,
      brokenImages: [...document.images].filter((img) => !img.complete || img.naturalWidth === 0).length,
      hiddenReadableContent: [...document.querySelectorAll('main h1, main h2, main h3, main p, main a')]
        .filter((el) => {
          const style = getComputedStyle(el)
          const rect = el.getBoundingClientRect()
          return el.textContent.trim() && rect.width > 1 && rect.height > 1 &&
            (style.visibility === 'hidden' || Number(style.opacity) === 0)
        }).length,
    }))
    if (!response?.ok()) errors.push(`HTTP ${response?.status()}`)
    if (health.overflow > 1) errors.push(`horizontal overflow ${health.overflow}px`)
    if (health.brokenImages) errors.push(`${health.brokenImages} broken images`)
    if (health.hiddenReadableContent) errors.push(`${health.hiddenReadableContent} readable nodes remain hidden`)
    if (errors.length) failures.push({ theme, width, errors, health })
    console.log(`${failures.length ? '·' : '✓'} ${theme} ${width}px`, health)
    await page.close()
  }
}

await browser.close()
if (failures.length) {
  console.error(JSON.stringify(failures, null, 2))
  process.exit(1)
}
console.log(`finalCThemeHealth: ${cases.length * viewports.length}/${cases.length * viewports.length} passed`)
