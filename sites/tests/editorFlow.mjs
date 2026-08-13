import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const choose = await readFile(new URL('../app/choose/[client]/page.jsx', import.meta.url), 'utf8')
const dashboard = await readFile(new URL('../app/dashboard/page.jsx', import.meta.url), 'utf8')
const site = await readFile(new URL('../app/site/[client]/page.jsx', import.meta.url), 'utf8')
const theme = await readFile(new URL('../app/site/[client]/theme.module.css', import.meta.url), 'utf8')
const connect = await readFile(new URL('../../web/connect.html', import.meta.url), 'utf8')
const landing = await readFile(new URL('../../web/index.html', import.meta.url), 'utf8')
const start = await readFile(new URL('../../web/start.html', import.meta.url), 'utf8')

assert.match(choose, /Διαμόρφωσέ το με live chat/)
assert.match(choose, /select-design/)
assert.match(choose, /dashboard\?client=/)
assert.match(dashboard, /new URLSearchParams\(window\.location\.search\)\.get\('client'\)/)
assert.match(dashboard, /emailRedirectTo: destination/)
assert.match(dashboard, /redirectTo: destination/)
assert.match(choose, /sessionStorage\.setItem\('vitrina-active-client', client\)/)
assert.match(dashboard, /sessionStorage\.getItem\('vitrina-active-client'\)/)
assert.match(dashboard, /if \(fromUrl && !pick\)/)
assert.doesNotMatch(dashboard, /owned\.find\(\(c\) => c\.id === fromUrl\) \|\| owned\[0\]/)
assert.match(dashboard, /Επεξεργάζεσαι/)
assert.match(dashboard, /Επίλεξε site για επεξεργασία/)
assert.match(dashboard, /setPhotos\(null\)/)
assert.match(dashboard, /pendingClient\(\)/)
assert.match(dashboard, /palette/)
assert.match(dashboard, /font_pair/)
assert.match(dashboard, /assetType = 'photo'/)
assert.match(dashboard, /asset_type', staged\.assetType/)
assert.match(dashboard, /Ανέβασε λογότυπο/)
assert.match(dashboard, /asset\.type === 'logo'/)
assert.match(dashboard, /logo-drafts/)
assert.match(choose, /3 προτάσεις λογοτύπου/)
assert.match(landing, /Logo Designer περιλαμβάνεται/)
assert.match(landing, /σου ετοιμάζουμε 3 προτάσεις/)
// «Site first, questions later» — η ροή που όρισε ο ιδιοκτήτης και υλοποιεί το
// `ccbfdb8` (11/8/2026): prompt → δημιουργία → preview → ερωτήσεις. Η αρχική ΔΕΝ
// ανοίγει φόρμα πριν ο πελάτης δει αποτέλεσμα· κάθε βήμα πριν την πρώτη «ουάου»
// στιγμή είναι σημείο διαρροής (βλ. docstring του `POST /start`).
//
// Το test έλεγχε ακόμη το ΠΑΛΙΟ `connect.html?desc=…&step=intake` και έμεινε
// κόκκινο δύο μέρες: κανείς δεν είχε συνδέσει το funnel με assertion που να
// αποτυγχάνει όταν αλλάζει η ροή, οπότε άλλαξε η ροή και έμεινε πίσω το test.
assert.match(landing, /start\.html\?text='\s*\+\s*encodeURIComponent/)
assert.doesNotMatch(landing, /connect\.html\?desc=/)

// Η αλυσίδα ολόκληρη, όχι μόνο το πρώτο βήμα: prompt → /start → claim → /choose.
// Χωρίς αυτά, μια σπασμένη μεταβίβαση ιδιοκτησίας περνάει αθόρυβα.
assert.match(start, /params\.get\('text'\)/)
assert.match(start, /fetch\(API \+ '\/start'/)
assert.match(start, /#claim=\$\{encodeURIComponent\(claimToken\)\}/)
assert.match(start, /\$\{SITES\}\/choose\/\$\{encodeURIComponent\(clientId\)\}/)

// Το connect.html παραμένει ζωντανό — OAuth callback και pilot intake — αλλά
// δεν είναι πια το κύριο funnel.
assert.match(connect, /Βήμα 2 — Συμπλήρωσε τα στοιχεία του μαγαζιού/)
assert.match(connect, /Δείξε μου τα σχέδια →/)
for (const businessType of ['Φαρμακείο', 'Γιατρός / Ιατρείο', 'Νύχια / Nail studio',
  'Κέντρο αισθητικής', 'Μασάζ / Wellness', 'Κατάστημα λιανικής',
  'Ενοικιαζόμενα δωμάτια', 'Συνεργείο αυτοκινήτων']) {
  assert.match(connect, new RegExp(`<option>${businessType.replace('/', '\\/')}</option>`))
}
assert.match(choose, /dashboard\?client=/)
assert.match(dashboard, /Δημιούργησε 3 προτάσεις/)
assert.match(dashboard, /Χρησιμοποίησέ το/)
assert.match(site, /data-palette=/)
assert.match(site, /data-font=/)
assert.match(site, /siteData\.palette \|\| siteData\.PALETTE/)
assert.match(site, /siteData\.font_pair \|\| siteData\.FONT_PAIR/)
assert.match(theme, /data-palette='forest'/)
assert.match(theme, /data-font='friendly'/)
assert.match(connect, /query\.has\('code'\)/)
assert.match(connect, /hash\.has\('access_token'\)/)
assert.match(connect, /sites-production-da56\.up\.railway\.app\/dashboard/)

console.log('editorFlow: theme selection -> live editor -> palette and typography preview passed')
