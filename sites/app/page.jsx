import Link from 'next/link'
import { TEMPLATE_KEYS, TEMPLATE_META } from '../lib/templates'
import { demoBusinesses } from '../lib/demoData'
import s from './page.module.css'

const DEMO_BY_TEMPLATE = {
  editorial: 'carpenter',
  split: 'lawyer',
  bento: 'cafe',
  longform: 'lawyer',
  poster: 'gym',
  sidebar: 'plumber',
  grid: 'dentist',
  magazine: 'taverna',
  warmth: 'taverna',
  ember: 'taverna',
  marble: 'dentist',
  runway: 'salon',
  forge: 'plumber',
  aegean: 'rooms',
  bloom: 'cafe',
  volt: 'gym',
  motor: 'garage',
  terra: 'farm',
  dispatch: 'plumber',
  canvas: 'carpenter',
}

export const metadata = {
  title: 'Vitrina — Το site της επιχείρησής σου, έτοιμο σε λεπτά',
  description: 'Δεκάδες όμορφα, responsive designs για ελληνικές τοπικές επιχειρήσεις. Διάλεξε, και είναι live.',
}

export default function Showcase() {
  return (
    <main className={s.page}>
      <header className={s.hero}>
        <span className={s.eyebrow}>Vitrina · Sites για ελληνικά μαγαζιά</span>
        <h1>Το site της επιχείρησής σου, <em>έτοιμο σε λεπτά.</em></h1>
        <p>Δεκάδες όμορφα, responsive designs. Διάλεξε αυτό που σου αρέσει — εμείς το ανεβάζουμε live στο δικό σου domain.</p>
        <div className={s.actions}>
          <a href="https://getvitrina.gr" className={s.btn}>Ξεκίνα τώρα</a>
          <a href="#designs" className={s.btnLine}>Δες τα designs ↓</a>
        </div>
        <div className={s.stats}>
          <div><b>{TEMPLATE_KEYS.length}+</b><span>έτοιμα designs</span></div>
          <div><b>Λεπτά</b><span>όχι εβδομάδες</span></div>
          <div><b>.gr</b><span>στο domain σου</span></div>
        </div>
      </header>

      <section className={s.features}>
        <div className={s.secHead}>
          <span className={s.eyebrow}>Τι παίρνεις</span>
          <h2>Όλη η online παρουσία σου, managed.</h2>
          <p className={s.secSub}>Όχι άλλο site από το 2014. Εμείς το στήνουμε, το κρατάμε online και το αλλάζουμε όποτε θες.</p>
        </div>
        <div className={s.featGrid}>
          <div className={s.feat}><span className={s.fi}>🌐</span><h3>Site που απαντά στα βασικά</h3><p>Πού είσαι, τι κάνεις, πώς σε βρίσκουν, πώς σε καλούν.</p></div>
          <div className={s.feat}><span className={s.fi}>🌍</span><h3>Domain .gr + hosting</h3><p>Δικό σου domain και φιλοξενία, όλα μέσα — χωρίς να ασχοληθείς.</p></div>
          <div className={s.feat}><span className={s.fi}>✏️</span><h3>Απεριόριστες αλλαγές</h3><p>Ζητάς με απλά λόγια, το αλλάζουμε εμείς. Δεν ανοίγεις ποτέ editor.</p></div>
          <div className={s.feat}><span className={s.fi}>🔍</span><h3>Local SEO</h3><p>Τίτλοι και λέξεις που ψάχνουν οι πελάτες στην πόλη σου.</p></div>
          <div className={s.feat}><span className={s.fi}>📍</span><h3>Χάρτης · τηλέφωνο · ώρες</h3><p>Τα στοιχεία που ψάχνει ο πελάτης, μπροστά — όχι κρυμμένα.</p></div>
          <div className={s.feat}><span className={s.fi}>⚡</span><h3>Concierge στήσιμο</h3><p>Το στήνουμε μαζί από μια περιγραφή. Δεν σε αφήνουμε με άδειο dashboard.</p></div>
        </div>
        <p className={s.soon}>🔜 Σύντομα: καθημερινά posts για Facebook &amp; Instagram (Φάση 2).</p>
      </section>

      <section id="designs" className={s.gridSec}>
        <div className={s.secHead}>
          <span className={s.eyebrow}>Η συλλογή</span>
          <h2>Διάλεξε το ύφος σου.</h2>
        </div>
        <div className={s.grid}>
          {TEMPLATE_KEYS.map((k) => {
            const bizKey = DEMO_BY_TEMPLATE[k] || 'carpenter'
            const biz = demoBusinesses[bizKey]
            const href = `/preview/${k}?biz=${bizKey}`
            return (
              <Link key={k} href={href} className={s.card} target="_blank">
                <div className={s.shot}>
                  <iframe src={href} title={`${biz.NAME} — ${TEMPLATE_META[k].label}`} loading="lazy" scrolling="no" />
                </div>
                <div className={s.cardBody}>
                  <span className={s.tag}>{biz.TRADE} · {TEMPLATE_META[k].label}</span>
                  <h3>{biz.NAME}</h3>
                  <p>{TEMPLATE_META[k].desc}</p>
                  <span className={s.open}>Άνοιξε το design →</span>
                </div>
              </Link>
            )
          })}
        </div>
      </section>

      <section className={s.cta}>
        <h2>Έτοιμος να αποκτήσεις το δικό σου;</h2>
        <p>Ένα site + καθημερινά posts. Χωρίς κόπο, στα ελληνικά.</p>
        <a href="https://getvitrina.gr" className={s.btn}>Ξεκίνα με τη Vitrina</a>
      </section>

      <footer className={s.footer}>© {new Date().getFullYear()} Vitrina · getvitrina.gr</footer>
    </main>
  )
}
