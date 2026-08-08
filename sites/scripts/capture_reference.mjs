#!/usr/bin/env node
/**
 * Vitrina Theme Builder — Phase 1 (Capture).
 *
 *    node sites/scripts/capture_reference.mjs <url> [--out <dir>] [--name <slug>]
 *
 * Ανοίγει το reference site σε πραγματικό browser και βγάζει ΜΕΤΡΗΣΕΙΣ, όχι
 * εντυπώσεις: computed CSS σε px, type scale, grid, spacing, radii, shadows,
 * breakpoints, sticky στοιχεία, animations — μαζί με full-page screenshots
 * σε desktop / tablet / mobile.
 *
 * Γιατί υπάρχει: χωρίς αυτό, η «πιστή ανακατασκευή» γίνεται εικασία από μια
 * εικόνα. Με αυτό ξέρουμε ότι το section padding είναι 96px και όχι «άνετο».
 *
 * Η έξοδος πάει ΕΚΤΟΣ repo by default. Τα screenshots ενός ξένου site είναι
 * υλικό ανάλυσης — δεν τα commit-άρουμε ποτέ.
 */
import { chromium, devices } from 'playwright'
import { mkdir, writeFile } from 'node:fs/promises'
import path from 'node:path'

const VIEWPORTS = [
  { id: 'desktop', width: 1440, height: 1024 },
  { id: 'tablet', width: 768, height: 1024 },
  { id: 'mobile', width: 390, height: 844 },
]

const args = process.argv.slice(2)
const url = args.find((a) => a.startsWith('http'))
const flag = (name, fallback) => {
  const i = args.indexOf(`--${name}`)
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback
}

if (!url) {
  console.error('Χρήση: node sites/scripts/capture_reference.mjs <url> [--out <dir>] [--name <slug>]')
  process.exit(1)
}

const slug = flag('name', new URL(url).hostname.replace(/^www\./, '').replace(/[^a-z0-9]+/gi, '-'))
const outDir = path.resolve(flag('out', path.join(process.env.TEMP || '/tmp', 'vitrina-refs', slug)))

/** Κατεβαίνει όλη τη σελίδα ώστε να φορτώσουν lazy images και scroll animations. */
async function settle(page) {
  await page.evaluate(async () => {
    const step = Math.round(window.innerHeight * 0.8)
    for (let y = 0; y < document.body.scrollHeight; y += step) {
      window.scrollTo(0, y)
      await new Promise((r) => setTimeout(r, 120))
    }
    window.scrollTo(0, 0)
    await new Promise((r) => setTimeout(r, 300))
  })
}

/** Όλα τα μετρήσιμα τρέχουν μέσα στη σελίδα — ένα πέρασμα, ένα JSON. */
const MEASURE = () => {
  const px = (v) => Math.round(parseFloat(v) || 0)
  const tally = (arr) => Object.entries(arr.reduce((acc, v) => {
    if (v) acc[v] = (acc[v] || 0) + 1
    return acc
  }, {})).sort((a, b) => b[1] - a[1])

  const all = [...document.querySelectorAll('*')].filter((el) => {
    const r = el.getBoundingClientRect()
    const cs = getComputedStyle(el)
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'
  })

  // ---------------------------------------------------------- τυπογραφία
  const textNodes = all.filter((el) =>
    [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim().length > 1))
  const typeScale = tally(textNodes.map((el) => {
    const cs = getComputedStyle(el)
    return [
      el.tagName.toLowerCase(),
      `${px(cs.fontSize)}px`,
      cs.fontWeight,
      `lh:${cs.lineHeight === 'normal' ? 'normal' : px(cs.lineHeight) + 'px'}`,
      `ls:${cs.letterSpacing === 'normal' ? '0' : cs.letterSpacing}`,
      cs.textTransform !== 'none' ? cs.textTransform : '',
      cs.fontFamily.split(',')[0].replace(/["']/g, ''),
    ].filter(Boolean).join(' · ')
  })).map(([style, count]) => ({ style, count }))

  // -------------------------------------------------------------- χρώματα
  const colors = {
    text: tally(textNodes.map((el) => getComputedStyle(el).color)).slice(0, 12),
    background: tally(all.map((el) => {
      const bg = getComputedStyle(el).backgroundColor
      return bg === 'rgba(0, 0, 0, 0)' ? null : bg
    })).slice(0, 12),
  }

  // ------------------------------------------------- δομή: top-level sections
  const root = document.querySelector('main') || document.body
  const SKIP = ['script', 'style', 'noscript', 'template', 'link']
  const sections = [...root.children].filter((el) =>
    !SKIP.includes(el.tagName.toLowerCase())).map((el, i) => {
    const r = el.getBoundingClientRect()
    const cs = getComputedStyle(el)
    const heading = el.querySelector('h1,h2,h3')
    const inner = [...el.querySelectorAll('*')]
      .map((c) => c.getBoundingClientRect().width)
      .filter((w) => w > 200 && w < r.width)
    return {
      order: i + 1,
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      class: (typeof el.className === 'string' ? el.className : '').slice(0, 80) || null,
      heightPx: Math.round(r.height),
      paddingTopPx: px(cs.paddingTop),
      paddingBottomPx: px(cs.paddingBottom),
      backgroundColor: cs.backgroundColor,
      contentWidthPx: inner.length ? Math.round(Math.max(...inner)) : null,
      headingTag: heading?.tagName.toLowerCase() || null,
      images: el.querySelectorAll('img,picture,video').length,
      links: el.querySelectorAll('a,button').length,
    }
  })

  // ----------------------------------------------------------- grid / layout
  const grids = all.filter((el) => {
    const d = getComputedStyle(el).display
    return d === 'grid' || d === 'flex'
  }).map((el) => {
    const cs = getComputedStyle(el)
    return `${cs.display} · cols:${cs.gridTemplateColumns === 'none' ? '-' : cs.gridTemplateColumns}` +
           ` · gap:${cs.gap === 'normal' ? '0' : cs.gap}`
  })

  // ------------------------------------------------------- ρυθμός αποστάσεων
  const spacing = tally(all.flatMap((el) => {
    const cs = getComputedStyle(el)
    return [cs.paddingTop, cs.paddingBottom, cs.marginTop, cs.marginBottom, cs.gap]
      .map((v) => px(v)).filter((n) => n >= 8).map((n) => `${n}px`)
  })).slice(0, 20)

  // ------------------------------------------------------- σχήματα & βάθος
  const radii = tally(all.map((el) => {
    const r = getComputedStyle(el).borderRadius
    return r === '0px' ? null : r
  })).slice(0, 10)
  const shadows = tally(all.map((el) => {
    const s = getComputedStyle(el).boxShadow
    return s === 'none' ? null : s
  })).slice(0, 10)

  // ------------------------------------------------------ εικόνες & αναλογίες
  const images = [...document.images].filter((i) => i.width > 80).map((i) => {
    const r = i.getBoundingClientRect()
    return {
      renderedPx: `${Math.round(r.width)}×${Math.round(r.height)}`,
      ratio: (r.width / r.height).toFixed(2),
      objectFit: getComputedStyle(i).objectFit,
      loading: i.loading || null,
      alt: (i.alt || '').slice(0, 60),
    }
  }).slice(0, 30)

  // ------------------------------------------------- sticky / fixed behaviour
  const pinned = all.filter((el) => ['sticky', 'fixed'].includes(getComputedStyle(el).position))
    .map((el) => {
      const cs = getComputedStyle(el)
      const r = el.getBoundingClientRect()
      return `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''} · ${cs.position}` +
             ` · top:${cs.top} · z:${cs.zIndex} · ${Math.round(r.width)}×${Math.round(r.height)}`
    }).slice(0, 12)

  // ------------------------------------------------- κίνηση & αλληλεπίδραση
  const motion = tally(all.flatMap((el) => {
    const cs = getComputedStyle(el)
    const out = []
    if (cs.transitionDuration !== '0s') {
      out.push(`transition ${cs.transitionProperty} ${cs.transitionDuration} ${cs.transitionTimingFunction}`)
    }
    if (cs.animationName !== 'none') {
      out.push(`animation ${cs.animationName} ${cs.animationDuration} ${cs.animationTimingFunction}`)
    }
    if (cs.transform !== 'none') out.push('transform')
    return out
  })).slice(0, 15)

  // ------------------------------------------------------------ breakpoints
  const breakpoints = new Set()
  const fontFaces = new Set()
  for (const sheet of document.styleSheets) {
    let rules
    try { rules = sheet.cssRules } catch { continue }  // cross-origin — δεν διαβάζεται
    const walk = (list) => {
      for (const rule of list) {
        if (rule.media?.mediaText) {
          breakpoints.add(rule.media.mediaText)
          if (rule.cssRules) walk(rule.cssRules)
        } else if (rule.constructor.name === 'CSSFontFaceRule') {
          fontFaces.add(rule.style.getPropertyValue('font-family').replace(/["']/g, ''))
        }
      }
    }
    walk(rules)
  }

  // ---------------------------------------------------------- design tokens
  const rootVars = {}
  for (const sheet of document.styleSheets) {
    let rules
    try { rules = sheet.cssRules } catch { continue }
    for (const rule of rules) {
      if (rule.selectorText === ':root' && rule.style) {
        for (const prop of rule.style) {
          if (prop.startsWith('--')) rootVars[prop] = rule.style.getPropertyValue(prop).trim()
        }
      }
    }
  }

  return {
    title: document.title,
    documentHeightPx: document.body.scrollHeight,
    sections,
    typeScale: typeScale.slice(0, 25),
    fontFamilies: tally([...textNodes].map((el) =>
      getComputedStyle(el).fontFamily.split(',')[0].replace(/["']/g, ''))).slice(0, 8),
    selfHostedFonts: [...fontFaces],
    colors,
    spacingRhythm: spacing,
    grids: tally(grids).slice(0, 15),
    radii,
    shadows,
    images,
    pinned,
    motion,
    breakpoints: [...breakpoints],
    cssVariables: rootVars,
  }
}

const main = async () => {
  await mkdir(outDir, { recursive: true })
  const browser = await chromium.launch()
  const report = { url, capturedAt: new Date().toISOString(), viewports: {} }

  for (const vp of VIEWPORTS) {
    // reducedMotion: τα scroll-driven animations αφήνουν κενά τμήματα στα
    // full-page screenshots. Την κίνηση τη διαβάζουμε από το computed CSS.
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 2,
      reducedMotion: 'reduce',
      userAgent: vp.id === 'mobile' ? devices['iPhone 13'].userAgent : undefined,
      isMobile: vp.id === 'mobile',
      hasTouch: vp.id !== 'desktop',
    })
    const page = await context.newPage()
    const errors = []
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text().slice(0, 160)))

    process.stdout.write(`  ${vp.id.padEnd(8)} ${vp.width}×${vp.height} … `)
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    } catch {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
    }
    await settle(page)

    const shot = path.join(outDir, `${vp.id}.png`)
    await page.screenshot({ path: shot, fullPage: true })
    const measured = await page.evaluate(MEASURE)
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > window.innerWidth + 1)

    report.viewports[vp.id] = { ...vp, ...measured, horizontalOverflow: overflow, consoleErrors: errors }
    console.log(`${measured.sections.length} sections · ${measured.documentHeightPx}px · ${path.basename(shot)}`)
    await context.close()
  }

  const jsonPath = path.join(outDir, 'measurements.json')
  await writeFile(jsonPath, JSON.stringify(report, null, 2), 'utf8')

  const d = report.viewports.desktop
  console.log(`\n${'─'.repeat(58)}\n${d.title}\n${'─'.repeat(58)}`)
  console.log(`Sections (desktop):`)
  for (const s of d.sections) {
    console.log(`  ${String(s.order).padStart(2)}. ${s.tag}${s.class ? '.' + s.class.split(' ')[0] : ''}` +
                ` — ${s.heightPx}px · padding ${s.paddingTopPx}/${s.paddingBottomPx}` +
                ` · content ${s.contentWidthPx || '?'}px · ${s.images} img · ${s.links} links`)
  }
  console.log(`\nΤυπογραφία (top 6):`)
  for (const t of d.typeScale.slice(0, 6)) console.log(`  ×${String(t.count).padStart(3)}  ${t.style}`)
  console.log(`\nΡυθμός αποστάσεων: ${d.spacingRhythm.slice(0, 8).map(([v, c]) => `${v}(×${c})`).join('  ')}`)
  console.log(`Breakpoints: ${d.breakpoints.join(' | ') || '—'}`)
  console.log(`Sticky/fixed: ${d.pinned.join('\n              ') || '—'}`)
  console.log(`\n📁 ${outDir}\n   measurements.json + desktop/tablet/mobile.png`)

  await browser.close()
}

main().catch((err) => {
  console.error(`\n✗ ${err.message}`)
  process.exit(1)
})
