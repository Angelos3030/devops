/**
 * FindUs — αντέχει σε στενό ΔΟΧΕΙΟ, όχι μόνο σε φαρδύ viewport.
 *
 *   node tests/findus_layout.mjs --base http://127.0.0.1:3881
 *
 * Γιατί υπάρχει: το κοινό FindUs ήταν grid `minmax(280px,1fr) 1.25fr` που
 * στοιβαζόταν ΜΟΝΟ με media query — δηλαδή όταν στένευε το viewport. Μετρήθηκε
 * σε πλάτος οθόνης 1440: το gymso έδινε στο FindUs 531px και το villa 555px,
 * οπότε η στήλη κειμένου καρφωνόταν στα 280px και του χάρτη έμεναν 107px —
 * ύψος 67px για περιεχόμενο 142px. Ο σύνδεσμος «κατευθείαν οδηγίες» και η
 * σημείωση εξαφανίζονταν, σε τρία themes ταυτόχρονα.
 *
 * Τρία themes, δύο viewports, επτά ελέγχοι· καθένας αντιστοιχεί σε πραγματικό
 * τρόπο με τον οποίο έσπασε ή θα μπορούσε να σπάσει το component.
 */
import { chromium } from 'playwright'

const arg = (n, d) => { const i = process.argv.indexOf(n); return i > -1 ? process.argv[i + 1] : d }
const BASE = arg('--base', 'http://127.0.0.1:3881')

// φαρδύ δοχείο · στενό δοχείο (η αιτία του σφάλματος) · στενό δοχείο #2
const CASES = [
  { tpl: 'medic-care', biz: 'physician', container: 'φαρδύ' },
  { tpl: 'gymso-fitness', biz: 'gym', container: 'στενό' },
  { tpl: 'villa-agency', biz: 'realestate', container: 'στενό' },
]
const VIEWPORTS = [['desktop', 1440, 900], ['mobile', 390, 844]]

const probe = () => {
  const wrap = document.querySelector('[class*="FindUs_wrap"]')
  if (!wrap) return { findus: false }
  const map = document.querySelector('[class*="FindUs_mapBox"]')
  const info = document.querySelector('[class*="FindUs_info"]')
  const W = (e) => (e ? Math.round(e.getBoundingClientRect().width) : 0)
  const box = map.getBoundingClientRect()

  const hidden = []
  for (const c of map.querySelectorAll('*')) {
    if (c.children.length || !(c.textContent || '').trim()) continue
    const r = c.getBoundingClientRect()
    const by = Math.round(Math.max(r.bottom - box.bottom, box.top - r.top,
                                   r.right - box.right, box.left - r.left))
    if (by > 2) hidden.push(`${(c.textContent || '').trim().slice(0, 24)} (-${by}px)`)
  }
  const links = [...wrap.querySelectorAll('a')].map((a) => {
    const r = a.getBoundingClientRect()
    return { href: a.getAttribute('href') || '', w: Math.round(r.width), h: Math.round(r.height) }
  })
  return {
    findus: true, wrapW: W(wrap), infoW: W(info), mapW: W(map),
    mapH: Math.round(box.height), clientH: map.clientHeight, scrollH: map.scrollHeight,
    sideBySide: info.getBoundingClientRect().bottom > box.top + 4 &&
                info.getBoundingClientRect().right <= box.left + 4,
    hidden, links,
  }
}

const run = async () => {
  const browser = await chromium.launch()
  const fails = []
  console.log('='.repeat(62))
  console.log('FindUs — συμπεριφορά σε στενό δοχείο')
  console.log('='.repeat(62))

  for (const { tpl, biz, container } of CASES) {
    for (const [label, width, height] of VIEWPORTS) {
      const ctx = await browser.newContext({ locale: 'el-GR', viewport: { width, height } })
      const page = await ctx.newPage()
      await page.goto(`${BASE}/preview/${tpl}?biz=${biz}`, { waitUntil: 'networkidle', timeout: 45000 })
      const r = await page.evaluate(probe)
      const bad = []

      if (!r.findus) {
        bad.push('το FindUs δεν αποδόθηκε καθόλου')
      } else {
        // D. καμία αποκοπή — ο λόγος που γράφτηκε αυτό το test
        if (r.scrollH - r.clientH > 2) bad.push(`αποκοπή ${r.scrollH - r.clientH}px`)
        // E. όλο το περιεχόμενο ορατό
        if (r.hidden.length) bad.push(`κρυμμένο κείμενο: ${r.hidden.join(', ')}`)
        // F. ο χάρτης παραμένει χρησιμοποιήσιμος, όχι σύμβολο
        if (r.mapW < 200 || r.mapH < 150) bad.push(`χάρτης πολύ μικρός: ${r.mapW}x${r.mapH}`)
        // G. οι σύνδεσμοι υπάρχουν και είναι πατήσιμοι
        const dirs = r.links.filter((l) => l.href.includes('maps'))
        if (!dirs.length) bad.push('χάθηκε ο σύνδεσμος οδηγιών')
        if (dirs.some((l) => l.w < 24 || l.h < 10)) bad.push('σύνδεσμος οδηγιών χωρίς μέγεθος')
        // A/B/C. φαρδύ δοχείο κρατά δύο στήλες· στενό στοιβάζεται
        if (label === 'desktop' && container === 'φαρδύ' && !r.sideBySide) {
          bad.push('το φαρδύ δοχείο έχασε τη διάταξη δύο στηλών')
        }
        if (container === 'στενό' && r.sideBySide) {
          bad.push(`στενό δοχείο (${r.wrapW}px) επιμένει σε δύο στήλες`)
        }
      }

      const tag = `${tpl} ${label}`.padEnd(28)
      console.log(`  ${bad.length ? '✗' : '✓'} ${tag} ${r.findus
        ? `wrap ${r.wrapW} · info ${r.infoW} · χάρτης ${r.mapW}x${r.mapH}` : ''}`)
      bad.forEach((x) => console.log(`      └ ${x}`))
      if (bad.length) fails.push(`${tpl}/${label}: ${bad.join(' | ')}`)
      await ctx.close()
    }
  }
  await browser.close()

  console.log('\n' + '='.repeat(62))
  if (fails.length) {
    console.log(`❌ ${fails.length} αποτυχίες:`)
    fails.forEach((f) => console.log(`   • ${f}`))
    process.exit(1)
  }
  console.log('✅ Το FindUs αντέχει και στα στενά δοχεία.')
}

run().catch((e) => { console.error(e); process.exit(1) })
