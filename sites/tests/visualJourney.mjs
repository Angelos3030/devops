#!/usr/bin/env node
import fs from 'node:fs/promises'
import path from 'node:path'
import { chromium } from 'playwright'

const args = process.argv.slice(2)
const at = (name, fallback) => {
  const i = args.indexOf(name)
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback
}
const BASE = at('--base', 'http://localhost:3800')
const OUT = path.resolve(at('--out', 'artifacts/visual-journey'))

const allCases = [
  { id: 'cafe', description: 'Έχω καφετέρια στη Μάνη με specialty καφέ και brunch', template: 'bakery-editorial', must: [/καφ|coffee|brunch/i], forbid: [/οδοντ|ντουλάπ|υδραυλ|μανικιούρ/i] },
  { id: 'taverna', description: 'Έχω παραδοσιακή ταβέρνα στη Θεσσαλονίκη', template: 'warmth', must: [/ταβέρν|φαγητ|μεζέ|σχάρα/i], forbid: [/οδοντ|ντουλάπ|μανικιούρ|φαρμακ/i] },
  { id: 'dentist', description: 'Έχω οδοντιατρείο στην Αθήνα', template: 'clinic-triage', must: [/οδοντ|χαμόγελο/i], forbid: [/κομμωτ|μανικιούρ|ντουλάπ|σχάρα/i] },
  { id: 'physician', description: 'Έχω παθολογικό ιατρείο στο Χαλάνδρι', template: 'clinic-triage', must: [/ιατρ|ασθεν|check-up|παθολογ/i], forbid: [/κομμωτ|μανικιούρ|ντουλάπ|σχάρα/i] },
  { id: 'pharmacy', description: 'Έχω φαρμακείο στον Γέρακα', template: 'quiet', must: [/φαρμακ|συνταγ|υγεία/i], forbid: [/ξυλουργ|κουζίνα|σχάρα|κομμωτ/i] },
  { id: 'nails', description: 'Έχω νυχάδικο στην Αθήνα', template: 'beauty-atelier', must: [/νύχ|μανικιούρ|πεντικιούρ|nail/i], forbid: [/κομμωτ|κούρεμα|μαλλι|οδοντ|υδραυλ|σχάρα|ντουλάπ/i] },
  { id: 'aesthetics', description: 'Έχω κέντρο αισθητικής στη Γλυφάδα', template: 'beauty-atelier', must: [/αισθητικ|επιδερμίδ|θεραπε/i], forbid: [/οδοντ|υδραυλ|σχάρα|ντουλάπ/i] },
  { id: 'massage', description: 'Έχω κέντρο μασάζ και ευεξίας στο Κουκάκι', template: 'living', must: [/μασάζ|ευεξ|χαλάρω/i], forbid: [/οδοντ|υδραυλ|σχάρα|ντουλάπ/i] },
  { id: 'carpenter', description: 'Ξυλουργός για κουζίνες και ντουλάπες', template: 'canvas', must: [/κουζίν|ντουλάπ|ξύλ|έπιπλ/i], forbid: [/οδοντ|μανικιούρ|σχάρα|φαρμακ/i] },
  { id: 'plumber', description: 'Υδραυλικός στην Αθήνα', template: 'callout', must: [/υδραυλ|βλάβ|επισκευ|κλήση/i], forbid: [/οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
  { id: 'retail', description: 'Έχω boutique γυναικείων ρούχων στη Νέα Σμύρνη', template: 'bento', must: [/boutique|ρούχ|συλλογ|styling/i], forbid: [/οδοντ|υδραυλ|σχάρα|ντουλάπ/i] },
  { id: 'lawyer', description: 'Έχω δικηγορικό γραφείο στην Αθήνα', template: 'marble', must: [/δικηγορ|νομικ|υπόθε/i], forbid: [/οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
  { id: 'rooms', description: 'Έχω ενοικιαζόμενα δωμάτια στην Πάρο', template: 'aegean', must: [/δωμάτι|διαμον|φιλοξεν/i, /πάρος|πάρου/i], forbid: [/νάξο|οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
  { id: 'gym', description: 'Έχω γυμναστήριο με personal training', template: 'volt', must: [/γυμναστ|προπόνη|training/i], forbid: [/οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
  { id: 'garage', description: 'Έχω συνεργείο αυτοκινήτων στον Πειραιά', template: 'motor', must: [/συνεργεί|αυτοκιν|service|όχημα/i], forbid: [/οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
  { id: 'farm', description: 'Είμαι παραγωγός ελαιολάδου στην Καλαμάτα', template: 'terra', must: [/παραγωγ|ελαιόλαδ|γη|προϊόν/i], forbid: [/οδοντ|μανικιούρ|σχάρα|ντουλάπ/i] },
]
const onlyCase = at('--case', '')
const cases = onlyCase ? allCases.filter((item) => item.id === onlyCase) : allCases
if (!cases.length) throw new Error(`Unknown visual journey case: ${onlyCase}`)

const failures = []
const check = (ok, label, detail = '') => {
  console.log(`  ${ok ? '✓' : '✗'} ${label}${detail ? ` — ${detail}` : ''}`)
  if (!ok) failures.push(`${label}${detail ? `: ${detail}` : ''}`)
}

await fs.mkdir(OUT, { recursive: true })
const browser = await chromium.launch()

for (const item of cases) {
  console.log(`\n[${item.id}] ${item.description}`)
  for (const viewport of [{ name: 'desktop', width: 1440, height: 1000 }, { name: 'mobile', width: 390, height: 844 }]) {
    const context = await browser.newContext({ viewport })
    const page = await context.newPage()
    const errors = []
    page.on('console', (msg) => msg.type() === 'error' && errors.push(msg.text()))
    page.on('pageerror', (err) => errors.push(err.message))
    page.setDefaultTimeout(10_000)
    const response = await page.goto(`${BASE}/preview/${item.template}?biz=${item.id}`, { waitUntil: 'domcontentloaded', timeout: 20_000 })
    await page.waitForTimeout(1500)
    await page.evaluate(async () => {
      for (let y = 0; y < document.body.scrollHeight; y += Math.max(320, window.innerHeight * 0.7)) {
        window.scrollTo(0, y)
        await new Promise((resolve) => setTimeout(resolve, 80))
      }
      window.scrollTo(0, 0)
    })
    await page.evaluate(async () => Promise.race([
      Promise.all([...document.images].map((image) => image.decode().catch(() => null))),
      new Promise((resolve) => setTimeout(resolve, 5000)),
    ]))
    const state = await page.evaluate(() => ({
      text: document.body.innerText.replace(/\s+/g, ' '),
      brokenImages: [...document.images].filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.src),
      images: [...document.images].map((image) => ({ src: image.currentSrc || image.src, alt: image.alt })),
      overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
      h1: document.querySelectorAll('h1').length,
    }))
    check(response?.ok(), `${viewport.name}: HTTP OK`, String(response?.status()))
    check(item.must.every((rule) => rule.test(state.text)), `${viewport.name}: σχετικό επαγγελματικό περιεχόμενο και τοποθεσία`)
    check(!item.forbid.some((rule) => rule.test(state.text)), `${viewport.name}: κανένα ξένο επάγγελμα`)
    check(state.brokenImages.length === 0, `${viewport.name}: όλες οι εικόνες φορτώνουν`, state.brokenImages.join(', '))
    check(state.images.length > 0, `${viewport.name}: έχει οπτικό υλικό`, String(state.images.length))
    check(!state.overflow, `${viewport.name}: χωρίς οριζόντιο overflow`)
    check(state.h1 === 1, `${viewport.name}: ακριβώς ένα H1`, String(state.h1))
    check(errors.length === 0, `${viewport.name}: χωρίς browser errors`, errors.join(' | '))
    await page.screenshot({ path: path.join(OUT, `${item.id}-${viewport.name}.png`), fullPage: true, timeout: 15_000 })
    await context.close()
  }
}

await browser.close()
console.log(`\nScreenshots: ${OUT}`)
if (failures.length) {
  console.error(`\nΑΠΟΤΥΧΙΕΣ (${failures.length})\n- ${failures.join('\n- ')}`)
  process.exit(1)
}
console.log(`\n✓ ${cases.length} επαγγέλματα πέρασαν πραγματικό browser/visual gate.`)
