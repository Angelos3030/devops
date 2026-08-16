// Ο guard εσωτερικής υπερχείλισης ξεχωρίζει ΣΧΕΔΙΟ από ΣΦΑΛΜΑ.
//
// Μετρημένο περιστατικό: στο Medic Care το h3::after είναι CSS τρίγωνο
// (right:-10px, border-width:10px 0 10px 10px) — το βελάκι της μαύρης ετικέτας
// του πρωτοτύπου. Έδινε +10px «υπερχείλιση» σε ΚΑΘΕ γύρο επιδιόρθωσης· το
// μοντέλο το κυνήγησε επί τέσσερα τρεξίματα και στην πορεία χάλασε το mobile
// (root +65px) ενώ διόρθωνε ένα σφάλμα που δεν υπήρχε.
//
// Το fixture έχει και τις δύο περιπτώσεις. Ο guard πρέπει να δει ΜΟΝΟ τη μία.
import { execFileSync } from 'node:child_process'
import assert from 'node:assert/strict'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const out = mkdtempSync(join(tmpdir(), 'ovf-'))
execFileSync('node', ['tests/shot-one.mjs', 'sites/tests/fixtures/overflow',
                      'index.html', 'fx', out], { encoding: 'utf8' })
const m = JSON.parse(execFileSync('node',
  ['-e', `process.stdout.write(require('fs').readFileSync(${JSON.stringify(join(out, 'fx-metrics.json'))},'utf8'))`],
  { encoding: 'utf8' }))

const found = m.desktop.innerOverflow
assert.equal(found.length, 1,
  `περίμενα ΑΚΡΙΒΩΣ μία υπερχείλιση (τη σπασμένη), βρήκα: ${JSON.stringify(found)}`)

// (1) το διακοσμητικό βελάκι είναι ακριβώς 10px — δεν πρέπει να εμφανίζεται
assert.ok(!/\+10px/.test(found[0]),
  `το διακοσμητικό ::after (+10px) δηλώθηκε ως σφάλμα: ${found[0]}`)

// (2) το πραγματικό παιδί ξεχειλίζει ~96px — πρέπει να πιαστεί
const px = Number(found[0].match(/\+(\d+)px/)[1])
assert.ok(px > 50, `η πραγματική υπερχείλιση δεν πιάστηκε σωστά: ${found[0]}`)

console.log(`overflowGuard: διακοσμητικό ::after αγνοήθηκε · πραγματική υπερχείλιση ${px}px πιάστηκε`)
