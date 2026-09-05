import { chromium } from 'playwright'
import fs from 'fs'
import path from 'path'

// Πακέτο λογοτύπου Vitrina — παραλλαγή Λ1-A «τεταρτημόριο».
// Το τζάμι ακουμπά την εσωτερική ακμή· εκεί έφυγε η ομοιότητα με picture-in-picture.
const OUT = 'c:/greek-smb-agent/research/logo/pack'
const INK = '#171714', PAPER = '#FBFAF7', CORAL = '#E85D3F'

// Γεωμετρία σε πλέγμα 26×26. Το πάχος γραμμής ανεβαίνει στα μικρά μεγέθη —
// κανονικό optical sizing, ίδιο σχέδιο.
const frame = (stroke, color) =>
  `<rect x="2" y="2" width="22" height="22" rx="4.4" fill="none" stroke="${color}" stroke-width="${stroke}"/>`
const pane = (color) =>
  `<path d="M13 13H22.7v6.5a3.1 3.1 0 0 1-3.1 3.1H13z" fill="${color}"/>`
const strokeFor = (px) => (px <= 24 ? 3 : px <= 40 ? 2.8 : 2.6)

const markSvg = (px, ink, paneColor) =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 26 26" width="${px}" height="${px}" role="img" aria-label="Vitrina">`
  + `<title>Vitrina</title>${frame(strokeFor(px), ink)}${pane(paneColor)}</svg>`

const dirs = ['svg', 'png/mark-coral', 'png/mark-dark', 'png/mark-light',
              'png/lockup-dark', 'png/lockup-light', 'social']
for (const d of dirs) fs.mkdirSync(path.join(OUT, d), { recursive: true })

// ── SVG: καθαρή γεωμετρία, καμία γραμματοσειρά, κανένα raster μέσα ──────
const svgs = {
  'vitrina-mark.svg': markSvg(64, INK, CORAL),
  'vitrina-mark-mono-dark.svg': markSvg(64, INK, INK),
  'vitrina-mark-mono-light.svg': markSvg(64, PAPER, PAPER),
  'vitrina-mark-currentcolor.svg':
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 26 26" width="64" height="64" role="img" aria-label="Vitrina">`
    + `<title>Vitrina</title>${frame(2.6, 'currentColor')}${pane('currentColor')}</svg>`,
}
for (const [n, s] of Object.entries(svgs)) fs.writeFileSync(path.join(OUT, 'svg', n), s + '\n')

const b = await chromium.launch()

async function shot(html, w, h, file, transparent) {
  const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 })
  await p.setContent(`<style>*{margin:0;padding:0;box-sizing:border-box}
    html,body{width:${w}px;height:${h}px;overflow:hidden}
    body{display:flex;align-items:center;justify-content:center;
    font-family:Manrope,system-ui,sans-serif;${transparent ? '' : ''}}</style>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@600&display=swap">${html}`)
  await p.evaluate(() => document.fonts.ready)
  await p.waitForTimeout(180)
  await p.screenshot({ path: file, omitBackground: !!transparent })
  await p.close()
}

// ── Σήμα μόνο του, διάφανο φόντο ───────────────────────────────────────
const SIZES = [16, 32, 48, 64, 96, 128, 180, 192, 256, 512, 1024, 2048]
for (const px of SIZES) {
  await shot(markSvg(px, INK, CORAL), px, px, `${OUT}/png/mark-coral/vitrina-mark-${px}.png`, true)
  await shot(markSvg(px, INK, INK), px, px, `${OUT}/png/mark-dark/vitrina-mark-dark-${px}.png`, true)
  await shot(markSvg(px, PAPER, PAPER), px, px, `${OUT}/png/mark-light/vitrina-mark-light-${px}.png`, true)
}

// ── Οριζόντιο lockup: σήμα + wordmark, διάφανο ─────────────────────────
const lockup = (h, ink, paneColor) => {
  const mk = Math.round(h * 0.86)
  return `<div style="display:inline-flex;align-items:center;gap:${Math.round(h * 0.4)}px;
    font-size:${h}px;font-weight:600;letter-spacing:-.03em;color:${ink};line-height:1">
    ${markSvg(mk, ink, paneColor)}vitrina</div>`
}
for (const h of [40, 80, 120, 200, 320]) {
  const w = Math.round(h * 5.2), hh = Math.round(h * 1.5)
  await shot(lockup(h, INK, CORAL), w, hh, `${OUT}/png/lockup-dark/vitrina-lockup-${h}.png`, true)
  await shot(lockup(h, PAPER, CORAL), w, hh, `${OUT}/png/lockup-light/vitrina-lockup-reversed-${h}.png`, true)
}

// ── Έτοιμα για social ──────────────────────────────────────────────────
const canvas = (bg, inner) =>
  `<div style="width:100%;height:100%;background:${bg};display:flex;align-items:center;justify-content:center">${inner}</div>`

// avatar: σήμα σε σκούρο, με αέρα γύρω
const avatar = (px) => canvas(INK,
  `<div style="width:${Math.round(px * 0.56)}px;height:${Math.round(px * 0.56)}px;display:flex">
     ${markSvg(Math.round(px * 0.56), PAPER, CORAL)}</div>`)
for (const px of [400, 512, 1024]) {
  await shot(avatar(px), px, px, `${OUT}/social/avatar-dark-${px}.png`, false)
  await shot(canvas(PAPER, markSvg(Math.round(px * 0.56), INK, CORAL)), px, px,
             `${OUT}/social/avatar-warm-${px}.png`, false)
}
// share / OG
await shot(canvas(PAPER, lockup(96, INK, CORAL)), 1200, 630, `${OUT}/social/share-1200x630.png`, false)
await shot(canvas(INK, lockup(96, PAPER, CORAL)), 1200, 630, `${OUT}/social/share-dark-1200x630.png`, false)
await shot(canvas(PAPER, lockup(110, INK, CORAL)), 1080, 1080, `${OUT}/social/instagram-1080.png`, false)
await shot(canvas(PAPER, lockup(130, INK, CORAL)), 1080, 1920, `${OUT}/social/story-1080x1920.png`, false)
await shot(canvas(PAPER, lockup(120, INK, CORAL)), 1640, 856, `${OUT}/social/facebook-cover-1640x856.png`, false)
await shot(canvas(INK, lockup(60, PAPER, CORAL)), 1128, 191, `${OUT}/social/linkedin-banner-1128x191.png`, false)

await b.close()

const count = (d) => fs.readdirSync(path.join(OUT, d)).length
console.log('svg          ', count('svg'))
console.log('mark PNG     ', count('png/mark-coral') + count('png/mark-dark') + count('png/mark-light'))
console.log('lockup PNG   ', count('png/lockup-dark') + count('png/lockup-light'))
console.log('social       ', count('social'))
