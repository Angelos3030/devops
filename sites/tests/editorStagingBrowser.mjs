import assert from 'node:assert/strict'
import { chromium } from 'playwright'

const app = process.env.QA_APP_URL
const api = process.env.QA_API_URL
const clientId = process.env.QA_CLIENT_ID
const session = JSON.parse(Buffer.from(process.env.QA_SESSION_B64, 'base64').toString('utf8'))
const storageKey = `sb-${new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).hostname.split('.')[0]}-auth-token`

async function content(token) {
  const response = await fetch(`${api}/clients/${clientId}/content`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const body = await response.text()
  assert.equal(response.status, 200, body)
  return JSON.parse(body)
}

async function applyFromPage(page, token, expectedVersion, phone, idempotencyKey) {
  return page.evaluate(async ({ api, clientId, token, expectedVersion, phone, idempotencyKey }) => {
    const response = await fetch(`${api}/clients/${clientId}/editor/apply`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Idempotency-Key': idempotencyKey,
      },
      body: JSON.stringify({
        expected_version: expectedVersion,
        idempotency_key: idempotencyKey,
        message: 'browser two-tab stale conflict',
        operations: [{ op: 'update_phone', params: { phone } }],
      }),
    })
    return { status: response.status, body: await response.text() }
  }, { api, clientId, token, expectedVersion, phone, idempotencyKey })
}

const browser = await chromium.launch({ headless: true })
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } })
await page.addInitScript(({ key, value }) => localStorage.setItem(key, value), {
  key: storageKey, value: JSON.stringify(session),
})

try {
  await page.goto(`${app}/dashboard?client=${clientId}`, { waitUntil: 'networkidle' })
  const composer = page.getByPlaceholder('Πες μου τι να αλλάξω…')
  await composer.waitFor({ state: 'visible', timeout: 30_000 })

  const initial = await content(session.access_token)
  const initialPhone = initial.content.phone

  await composer.fill('Άλλαξε το τηλέφωνο σε 210 111 2233')
  await composer.press('Enter')
  await page.getByText('Οι αλλαγές είναι σε προεπισκόπηση').waitFor({ timeout: 70_000 })
  let persisted = await content(session.access_token)
  assert.equal(persisted.content.phone, initialPhone, 'proposal mutated state before approval')

  await page.getByRole('button', { name: 'Απόρριψη' }).click()
  await page.reload({ waitUntil: 'networkidle' })
  await composer.waitFor({ state: 'visible', timeout: 30_000 })
  persisted = await content(session.access_token)
  assert.equal(persisted.content.phone, initialPhone, 'reject + refresh mutated state')
  console.log('  PASS  proposal -> reject -> refresh leaves zero mutation')

  await composer.fill('allakse to tilefono se 210 111 2233')
  await composer.press('Enter')
  await page.getByText('Οι αλλαγές είναι σε προεπισκόπηση').waitFor({ timeout: 70_000 })
  await page.getByRole('button', { name: 'Έγκριση αλλαγών' }).click()
  await page.getByText('Οι αλλαγές εγκρίθηκαν και αποθηκεύτηκαν στο site σου.').waitFor({ timeout: 30_000 })
  persisted = await content(session.access_token)
  assert.equal(persisted.content.phone.replace(/\s/g, ''), '2101112233')
  const committedVersion = persisted.editor_version

  await page.reload({ waitUntil: 'networkidle' })
  await composer.waitFor({ state: 'visible', timeout: 30_000 })
  persisted = await content(session.access_token)
  assert.equal(persisted.editor_version, committedVersion)
  assert.equal(persisted.content.phone.replace(/\s/g, ''), '2101112233')
  console.log('  PASS  message -> proposal -> approve -> refresh persists state')

  await composer.fill('όχι, γύρνα πίσω την τελευταία αλλαγή')
  await composer.press('Enter')
  await page.getByText('Η τελευταία αλλαγή αναιρέθηκε.').waitFor({ timeout: 30_000 })
  await page.reload({ waitUntil: 'networkidle' })
  await composer.waitFor({ state: 'visible', timeout: 30_000 })
  persisted = await content(session.access_token)
  assert.equal(persisted.content.phone, initialPhone)
  assert.equal(persisted.editor_version, committedVersion + 1)
  console.log('  PASS  undo -> refresh restores exact state')

  const secondTab = await browser.newPage({ viewport: { width: 1440, height: 900 } })
  await secondTab.addInitScript(({ key, value }) => localStorage.setItem(key, value), {
    key: storageKey, value: JSON.stringify(session),
  })
  await secondTab.goto(`${app}/dashboard?client=${clientId}`, { waitUntil: 'networkidle' })
  await secondTab.getByPlaceholder('Πες μου τι να αλλάξω…').waitFor({ state: 'visible', timeout: 30_000 })

  const sharedVersion = persisted.editor_version
  const firstTabResult = await applyFromPage(
    page, session.access_token, sharedVersion, '2103334455', `browser-tab-a-${Date.now()}`,
  )
  assert.equal(firstTabResult.status, 200, firstTabResult.body)
  const staleTabResult = await applyFromPage(
    secondTab, session.access_token, sharedVersion, '2109998877', `browser-tab-b-${Date.now()}`,
  )
  assert.equal(staleTabResult.status, 409, staleTabResult.body)

  persisted = await content(session.access_token)
  assert.equal(persisted.content.phone, '2103334455', 'stale tab overwrote the winning edit')
  const undoResponse = await page.evaluate(async ({ api, clientId, token, expectedVersion }) => {
    const response = await fetch(`${api}/clients/${clientId}/editor/undo`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ expected_version: expectedVersion, idempotency_key: `browser-undo-${Date.now()}` }),
    })
    return { status: response.status, body: await response.text() }
  }, { api, clientId, token: session.access_token, expectedVersion: persisted.editor_version })
  assert.equal(undoResponse.status, 200, undoResponse.body)
  persisted = await content(session.access_token)
  assert.equal(persisted.content.phone, initialPhone)
  await secondTab.close()
  console.log('  PASS  two tabs -> first commit wins -> stale tab gets 409 -> no lost update')

  await page.screenshot({ path: 'research/ai-editor/staging-browser-proof.png', fullPage: true })
  console.log('\nEDITOR BROWSER STAGING: PASS (4/4)')
} finally {
  await browser.close()
}
