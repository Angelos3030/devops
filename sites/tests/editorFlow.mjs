import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const choose = await readFile(new URL('../app/choose/[client]/page.jsx', import.meta.url), 'utf8')
const dashboard = await readFile(new URL('../app/dashboard/page.jsx', import.meta.url), 'utf8')

assert.match(choose, /Διαμόρφωσέ το με live chat/)
assert.match(choose, /select-design/)
assert.match(choose, /dashboard\?client=/)
assert.match(dashboard, /new URLSearchParams\(window\.location\.search\)\.get\('client'\)/)
assert.match(dashboard, /emailRedirectTo: destination/)
assert.match(dashboard, /redirectTo: destination/)

console.log('editorFlow: theme selection -> secure live-chat dashboard redirect passed')
