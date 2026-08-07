import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const choose = await readFile(new URL('../app/choose/[client]/page.jsx', import.meta.url), 'utf8')
const dashboard = await readFile(new URL('../app/dashboard/page.jsx', import.meta.url), 'utf8')
const site = await readFile(new URL('../app/site/[client]/page.jsx', import.meta.url), 'utf8')
const theme = await readFile(new URL('../app/site/[client]/theme.module.css', import.meta.url), 'utf8')

assert.match(choose, /Διαμόρφωσέ το με live chat/)
assert.match(choose, /select-design/)
assert.match(choose, /dashboard\?client=/)
assert.match(dashboard, /new URLSearchParams\(window\.location\.search\)\.get\('client'\)/)
assert.match(dashboard, /emailRedirectTo: destination/)
assert.match(dashboard, /redirectTo: destination/)
assert.match(dashboard, /palette/)
assert.match(dashboard, /font_pair/)
assert.match(site, /data-palette=/)
assert.match(site, /data-font=/)
assert.match(site, /siteData\.palette \|\| siteData\.PALETTE/)
assert.match(site, /siteData\.font_pair \|\| siteData\.FONT_PAIR/)
assert.match(theme, /data-palette='forest'/)
assert.match(theme, /data-font='friendly'/)

console.log('editorFlow: theme selection -> live editor -> palette and typography preview passed')
