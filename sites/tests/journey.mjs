/**
 * Ο ΠΕΛΑΤΗΣ, ΣΕ ΠΡΑΓΜΑΤΙΚΟ BROWSER.
 *
 *   node tests/journey.mjs                 # στο ζωντανό
 *   node tests/journey.mjs --local         # σε localhost:3000 + :8000
 *   node tests/journey.mjs --headed        # με ανοιχτό παράθυρο, να το βλέπεις
 *
 * Το scripts/e2e.py χτυπάει URLs — βλέπει αν ο server απαντάει. Αυτό εδώ κάνει
 * ό,τι κάνει άνθρωπος: μπαίνει, πατάει, γράφει, αποθηκεύει, βγαίνει, ξαναμπαίνει.
 * Πιάνει ό,τι δεν πιάνει το άλλο: σπασμένο κουμπί, αλλαγή που δεν φτάνει στο
 * site, tracker που φορτώνει κρυφά, δεδομένα που μένουν ορατά μετά το logout.
 *
 * Φτιάχνει δικό του πελάτη και τον σβήνει στο τέλος — δεν αγγίζει αληθινούς.
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import { readFileSync } from 'node:fs'

const LOCAL = process.argv.includes('--local')
const HEADED = process.argv.includes('--headed')
const API = LOCAL ? 'http://localhost:8000' : 'https://devops-production-d563.up.railway.app'
const SITES = LOCAL ? 'http://localhost:3000' : 'https://sites-production-da56.up.railway.app'
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36'

// Domains που δεν επιτρέπεται να χτυπηθούν χωρίς συγκατάθεση του επισκέπτη.
const TRACKERS = ['googleapis.com', 'gstatic.com', 'google-analytics.com',
                  'googletagmanager.com', 'facebook.net', 'doubleclick.net']

const env = Object.fromEntries(
  readFileSync(new URL('../../.env', import.meta.url), 'utf8')
    .split(/\r?\n/).filter((l) => /^[A-Z_]+=/.test(l))
    .map((l) => [l.slice(0, l.indexOf('=')), l.slice(l.indexOf('=') + 1).trim()]))

const pass = [], fail = []
const check = (name, ok, detail = '') => {
  ;(ok ? pass : fail).push(name)
  console.log(`  ${ok ? '✓' : '✗'} ${name}${detail ? `  — ${detail}` : ''}`)
  return ok
}
const api = async (path, opts = {}) => {
  const r = await fetch(API + path, {
    ...opts,
    headers: { 'User-Agent': UA, 'Content-Type': 'application/json', ...(opts.headers || {}) },
  })
  return [r.status, await r.text()]
}

async function main() {
  const stamp = Date.now()
  const email = `journey+${stamp}@getvitrina.gr`
  const NAME = 'ΔΟΚΙΜΗ JOURNEY'
  let clientId = null, userId = null, browser = null

  const sb = createClient(env.SUPABASE_URL, env.SUPABASE_KEY,
    { auth: { autoRefreshToken: false, persistSession: false } })

  try {
    console.log('='.repeat(64))
    console.log(`VITRINA — ο πελάτης σε πραγματικό browser  (${LOCAL ? 'τοπικά' : 'ζωντανά'})`)
    console.log('='.repeat(64))

    // ---------------------------------------------------------------- setup
    console.log('\n[ΣΤΗΣΙΜΟ]')
    const [c, body] = await api('/onboard', {
      method: 'POST',
      body: JSON.stringify({ name: NAME, type: 'Ταβέρνα', city: 'Καλαμαριά',
                             phone: '2310 000000', email }),
    })
    if (!check('δημιουργήθηκε πελάτης', c === 200, body.slice(0, 90))) return
    clientId = JSON.parse(body).client_id

    const { data: u, error: uErr } = await sb.auth.admin.createUser(
      { email, email_confirm: true })
    if (!check('δημιουργήθηκε λογαριασμός', !uErr, uErr?.message || '')) return
    userId = u.user.id

    const { data: link, error: lErr } = await sb.auth.admin.generateLink(
      { type: 'magiclink', email })
    if (!check('βγήκε σύνδεσμος σύνδεσης', !lErr, lErr?.message || '')) return

    browser = await chromium.launch({ headless: !HEADED })
    const ctx = await browser.newContext({ userAgent: UA, locale: 'el-GR' })
    const page = await ctx.newPage()

    // --------------------------------------------- το site: τι φορτώνει όντως
    console.log('\n[ΙΔΙΩΤΙΚΟΤΗΤΑ] Τι ζητάει το site χωρίς να το ξέρει ο επισκέπτης')
    const third = new Set()
    page.on('request', (r) => {
      const h = new URL(r.url()).hostname
      if (TRACKERS.some((t) => h.endsWith(t)) || h.endsWith('google.com')) third.add(h)
    })
    await page.goto(`${SITES}/site/${clientId}`, { waitUntil: 'networkidle' })
    check('το site φορτώνει', await page.locator('body').isVisible())
    check('δείχνει το όνομα', (await page.content()).includes('ΔΟΚΙΜΗ'))
    check('ΚΑΝΕΝΑ αίτημα σε Google/Meta', third.size === 0, [...third].join(', '))

    const cookies = await ctx.cookies()
    check('κανένα cookie πριν από συγκατάθεση', cookies.length === 0,
          cookies.map((k) => k.name).join(', '))

    const fontOK = await page.evaluate(() => document.fonts.check('16px Fraunces'))
    check('τα ελληνικά fonts φορτώνουν τοπικά', fontOK)

    // ο χάρτης φορτώνει ΜΟΝΟ με κλικ
    const holder = page.locator('#find-us button').first()
    if (await holder.count()) {
      check('ο χάρτης δεν έχει φορτώσει μόνος του',
            (await page.locator('#find-us iframe').count()) === 0)
      await holder.click()
      await page.waitForTimeout(1200)
      check('μετά το κλικ εμφανίζεται ο χάρτης',
            (await page.locator('#find-us iframe').count()) === 1)
    }

    // --------------------------------------------------------------- login
    console.log('\n[ΣΥΝΔΕΣΗ] Ο πελάτης μπαίνει')
    const target = new URL(link.properties.action_link)
    target.searchParams.set('redirect_to', `${SITES}/dashboard`)
    await page.goto(target.toString(), { waitUntil: 'networkidle' })
    await page.waitForTimeout(2500)
    check('βρέθηκε στο dashboard', page.url().includes('/dashboard'), page.url())
    check('βλέπει το site του', (await page.locator('iframe').count()) > 0)

    // ------------------------------------------------------------ αλλαγή
    console.log('\n[ΑΛΛΑΓΗ] Αλλάζει κάτι μόνος του')
    await page.getByRole('button', { name: /Στοιχεία/ }).click()
    const phone = page.locator('label', { hasText: 'Τηλέφωνο' }).locator('input')
    await phone.waitFor({ timeout: 15000 })
    const NEW_PHONE = `2310 ${String(stamp).slice(-6)}`
    await phone.fill(NEW_PHONE)
    await page.getByRole('button', { name: /Αποθήκευση/ }).click()
    await page.waitForTimeout(3500)
    check('η αποθήκευση επιβεβαιώθηκε',
          (await page.locator('body').innerText()).match(/Αποθηκεύτηκ|Έγινε|✓/) !== null)

    const [, after] = await api(`/clients/${clientId}/site-data`)
    check('η αλλαγή έφτασε στο site', after.includes(NEW_PHONE),
          after.includes(NEW_PHONE) ? '' : 'το site δείχνει ακόμα το παλιό')

    // -------------------------------------------------------------- posts
    console.log('\n[POSTS] Χωρίς πακέτο βλέπει δείγμα, όχι κενό')
    await page.getByRole('button', { name: /Posts/ }).click()
    await page.waitForTimeout(3000)
    const posts = await page.locator('body').innerText()
    check('εμφανίζεται τουλάχιστον ένα post', /Δευτέρα|Αντιγραφή/.test(posts))
    check('υπάρχει πρόταση αναβάθμισης', /29[,.]99|Ξεκλείδωσ/.test(posts))
    check('υπάρχει σύνδεσμος για τον οδηγό Facebook',
          (await page.locator('a[href="/odigos/facebook"]').count()) > 0)

    // --------------------------------------------------------------- chat
    console.log('\n[CHAT] Η καρτέλα απαντά (ή το λέει καθαρά)')
    await page.getByRole('button', { name: /Πες μου/ }).click()
    await page.waitForTimeout(800)
    check('υπάρχει πεδίο συνομιλίας', (await page.locator('input[placeholder*="αλλάξω"]').count()) > 0)

    // ------------------------------------------------------------- έξοδος
    console.log('\n[ΕΞΟΔΟΣ] Και ξαναμπαίνει')
    await page.getByRole('button', { name: /Έξοδος|Αποσύνδεση/ }).first().click()
    await page.waitForTimeout(2500)
    const out = await page.locator('body').innerText()
    check('βγήκε — δεν φαίνονται πια τα δεδομένα του', !out.includes(NEW_PHONE))
    check('βλέπει οθόνη σύνδεσης', /σύνδεσ|email|Google/i.test(out))

    await page.goto(`${SITES}/dashboard`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(2000)
    check('μετά το logout το dashboard ζητάει ξανά σύνδεση',
          !(await page.locator('body').innerText()).includes(NEW_PHONE))
  } catch (e) {
    check(`απρόσμενο σφάλμα: ${e.message.split('\n')[0]}`, false)
  } finally {
    if (browser) await browser.close()
    console.log('\n[ΚΑΘΑΡΙΣΜΟΣ]')
    if (userId) {
      const { error } = await sb.auth.admin.deleteUser(userId)
      check('ο δοκιμαστικός λογαριασμός διαγράφηκε', !error, error?.message || '')
    }
    if (clientId) {
      const { error } = await sb.from('clients').delete().eq('id', clientId)
      check('ο δοκιμαστικός πελάτης διαγράφηκε', !error, error?.message || '')
      if (error) console.log(`    ⚠ σβήσε χειροκίνητα: ${clientId}`)
    }
    console.log('\n' + '='.repeat(64))
    console.log(`ΠΕΡΑΣΑΝ: ${pass.length}   ΕΣΠΑΣΑΝ: ${fail.length}`)
    if (fail.length) {
      console.log('\n❌ ΠΡΟΒΛΗΜΑΤΑ:')
      fail.forEach((f) => console.log(`   • ${f}`))
    } else {
      console.log('\n✅ Ο πελάτης μπορεί να κάνει τη δουλειά του μόνος.')
    }
    process.exit(fail.length ? 1 : 0)
  }
}

main()
