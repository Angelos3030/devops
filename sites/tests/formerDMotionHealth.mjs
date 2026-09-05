import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const base = process.env.QA_BASE || 'http://127.0.0.1:3900'
const root = path.resolve(process.cwd(), '..')
const output = path.join(root, 'research', 'visual-theme-audit', 'remediated', 'motion-health.json')
const themes = {
  aegean: 'rooms', bloom: 'aesthetics', canvas: 'farm', ember: 'taverna',
  forge: 'carpenter', marble: 'pharmacy', motor: 'garage', pulse: 'gym',
  runway: 'gym', terra: 'farm',
}

const browser = await chromium.launch({ headless: true })
const results = []

for (const [id, biz] of Object.entries(themes)) {
  const theme = { id, biz, viewports: {} }
  for (const [label, width, height] of [['desktop', 1440, 1024], ['mobile', 390, 844]]) {
    const page = await browser.newPage({
      viewport: { width, height },
      deviceScaleFactor: 1,
      reducedMotion: 'no-preference',
    })
    const consoleErrors = []
    const pageErrors = []
    page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()) })
    page.on('pageerror', (error) => pageErrors.push(error.message))
    await page.addInitScript(() => {
      window.__vitrinaLayoutShifts = []
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) window.__vitrinaLayoutShifts.push(entry.value)
        }
      }).observe({ type: 'layout-shift', buffered: true })
    })
    const response = await page.goto(`${base}/preview/${id}?biz=${biz}`, {
      waitUntil: 'networkidle', timeout: 45_000,
    })
    await page.evaluate(async () => {
      await Promise.race([
        Promise.all([document.fonts.ready.catch(() => null), ...[...document.images].map((img) => img.decode().catch(() => null))]),
        new Promise((resolve) => setTimeout(resolve, 8_000)),
      ])
      window.__vitrinaLayoutShifts = []
    })

    const candidates = await page.locator('*').evaluateAll((nodes) => nodes
      .map((element, index) => {
        const style = getComputedStyle(element)
        const timeline = style.animationTimeline || ''
        if (!timeline.includes('view')) return null
        const rect = element.getBoundingClientRect()
        return { index, tag: element.tagName, className: String(element.className).slice(0, 140), y: rect.y + scrollY }
      })
      .filter(Boolean))

    const samples = []
    for (const candidate of candidates) {
      const locator = page.locator('*').nth(candidate.index)
      if (!await locator.count()) continue
      const geometry = await locator.evaluate((element) => {
        const rect = element.getBoundingClientRect()
        return { top: rect.top + scrollY, height: rect.height }
      }).catch(() => null)
      if (!geometry) continue
      const activationPositions = await page.evaluate(({ top, elementHeight }) => {
        const viewport = innerHeight
        return [
          top - viewport * 0.8,
          top - viewport * 0.55,
          top - viewport * 0.3,
          top + elementHeight * 0.2 - viewport * 0.5,
        ].map((value) => Math.max(0, value))
      }, { top: geometry.top, elementHeight: geometry.height })
      const activationSamples = []
      for (const y of activationPositions) {
        await page.evaluate((nextY) => scrollTo(0, nextY), y)
        await page.waitForTimeout(100)
        activationSamples.push(await locator.evaluate((element) => Number(getComputedStyle(element).opacity)).catch(() => 0))
      }
      const bestIndex = activationSamples.indexOf(Math.max(...activationSamples))
      await page.evaluate((nextY) => scrollTo(0, nextY), activationPositions[Math.max(0, bestIndex)])
      await page.waitForTimeout(180)
      const first = await locator.evaluate((element) => {
        const rect = element.getBoundingClientRect()
        const style = getComputedStyle(element)
        return { opacity: Number(style.opacity), y: rect.y, height: rect.height, visibility: style.visibility }
      }).catch(() => null)
      await page.waitForTimeout(260)
      const second = await locator.evaluate((element) => {
        const rect = element.getBoundingClientRect()
        const style = getComputedStyle(element)
        return { opacity: Number(style.opacity), y: rect.y, height: rect.height, visibility: style.visibility }
      }).catch(() => null)
      if (!first || !second) continue
      samples.push({
        tag: candidate.tag,
        className: candidate.className,
        maxActivationOpacity: Math.max(...activationSamples),
        becomesVisible: Math.max(...activationSamples) > 0.05,
        visibleOnEntry: first.opacity >= 0.95 && first.visibility !== 'hidden' && first.height > 1,
        remainsVisible: second.opacity >= 0.95 && second.visibility !== 'hidden' && second.height > 1,
        movement: Math.abs(second.y - first.y),
      })
    }

    const pageState = await page.evaluate(() => ({
      layoutShiftScore: (window.__vitrinaLayoutShifts || []).reduce((sum, value) => sum + value, 0),
      horizontalOverflow: document.documentElement.scrollWidth - innerWidth,
    }))
    theme.viewports[label] = {
      status: response?.status() || 0,
      candidateCount: candidates.length,
      visibleOnEntry: samples.filter((sample) => sample.visibleOnEntry).length,
      remainsVisible: samples.filter((sample) => sample.remainsVisible).length,
      maxMovement: samples.length ? Math.max(...samples.map((sample) => sample.movement)) : 0,
      consoleErrors,
      pageErrors,
      ...pageState,
      failures: samples.filter((sample) => !sample.becomesVisible || !sample.visibleOnEntry || !sample.remainsVisible || sample.movement > 2),
    }
    await page.close()
  }
  results.push(theme)
  console.log(`[motion] ${id}`)
}

await browser.close()
fs.mkdirSync(path.dirname(output), { recursive: true })
fs.writeFileSync(output, JSON.stringify({ base, generatedAt: new Date().toISOString(), themes: results }, null, 2))
console.log(`motion health: ${results.length} themes -> ${output}`)
