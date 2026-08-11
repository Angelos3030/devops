// Client component: η φόρμα χρειάζεται κατάσταση. Είναι το ΜΟΝΟ template με
// διαδραστικό στοιχείο, οπότε το κόστος υδροποίησης μένει εδώ και δεν αγγίζει
// τα υπόλοιπα 35.
'use client'
import { useState } from 'react'
import s from './Callout.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Callout" — για τεχνίτες: υδραυλικός, ηλεκτρολόγος, ψυκτικός.
// Το ζητούμενο δεν είναι να θαυμάσει κανείς το site· είναι να σηκώσει τηλέφωνο
// τώρα, γιατί κάτι έχει σπάσει. Signature: κάρτα «ζήτησε προσφορά» πάνω στο hero,
// με το τηλέφωνο μεγάλο δίπλα της — δύο δρόμοι στην ίδια οθόνη.
//
// ΟΧΙ ψεύτικα στοιχεία εμπιστοσύνης: κανένα λογότυπο Google/Facebook/πιστοποίησης.
// Το «24/7» εμφανίζεται ΜΟΝΟ αν το ωράριο του πελάτη το λέει όντως.

const ROUND_THE_CLOCK = /24\s*[\/\-]?\s*7|24ωρ|24 ωρ|ολο το 24|όλο το 24|εικοσιτετρ/i

const SEGMENTS = [
  { key: 'home', title: 'Στο σπίτι', desc: 'Βλάβες, συντήρηση, μικροεπισκευές' },
  { key: 'shop', title: 'Στην επιχείρηση', desc: 'Καταστήματα, γραφεία, κουζίνες' },
  { key: 'plan', title: 'Προγραμματισμένη δουλειά', desc: 'Ανακαίνιση ή νέα εγκατάσταση' },
]

export default function Callout({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const services = Array.isArray(d.services) ? d.services.slice(0, 6) : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 3) : []
  const always = ROUND_THE_CLOCK.test(String(d.HOURS || ''))

  // Η φόρμα δεν έχει server. Συνθέτει μήνυμα προς τον ΙΔΙΟ τον πελάτη — έτσι
  // δουλεύει πραγματικά, δεν στέλνει δεδομένα σε τρίτους, και δεν υπόσχεται
  // παραλαβή που δεν μπορούμε να εγγυηθούμε. Χωρίς email, μένει το τηλέφωνο.
  const [form, setForm] = useState({ name: '', phone: '', need: '' })
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const canMail = Boolean(d.EMAIL)

  function submit(e) {
    e.preventDefault()
    const url = buildQuoteMailto({ email: d.EMAIL, ...form })
    window.location.href = url || tel
  }

  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#services">{d.SERVICES_NAV || 'Υπηρεσίες'}</a>
          <a href="#areas">Περιοχές</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && <img className={s.heroImg} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />}
        <span className={s.heroVeil} aria-hidden="true" />

        <div className={s.heroInner}>
          <div className={s.heroCopy}>
            {d.KICKER && <span className={s.eyebrow}>{d.KICKER}</span>}
            <h1 className={s.title}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
            {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}

            <div className={s.callBlock}>
              <span className={s.callLabel}>
                {always ? 'Τηλέφωνο βλάβης · 24/7' : 'Πάρε τηλέφωνο'}
              </span>
              <a href={tel} className={s.callNumber}>{d.PHONE}</a>
              {d.AREAS && <span className={s.callAreas}>{d.AREAS}</span>}
            </div>
          </div>

          {/* Το σήμα κατατεθέν: η φόρμα κάθεται ΠΑΝΩ στο hero, όχι στο τέλος.
              Χωρίς email του πελάτη ΔΕΝ δείχνουμε πεδία — θα ήταν φόρμα που δεν
              πάει πουθενά. Μένει κάρτα κλήσης, που είναι και το πιο γρήγορο. */}
          {!canMail ? (
            <div className={s.quote}>
              <h2 className={s.quoteTitle}>Χρειάζεσαι τεχνίτη τώρα;</h2>
              <p className={s.quoteSub}>Πάρε τηλέφωνο και τα λέμε αμέσως.</p>
              <a href={tel} className={s.quoteBtn} role="button">{d.PHONE}</a>
              {d.HOURS && <span className={s.quoteAlt}>{d.HOURS}</span>}
            </div>
          ) : (
          <form className={s.quote} onSubmit={submit}>
            <h2 className={s.quoteTitle}>Ζήτησε προσφορά</h2>
            <p className={s.quoteSub}>Συμπλήρωσε δύο στοιχεία και σου απαντάμε.</p>
            <label className={s.field}>
              <span>Το όνομά σου</span>
              <input value={form.name} onChange={set('name')} required
                     autoComplete="name" placeholder="Γιώργος" />
            </label>
            <label className={s.field}>
              <span>Τηλέφωνο</span>
              <input value={form.phone} onChange={set('phone')} required
                     type="tel" inputMode="tel" autoComplete="tel" placeholder="69…" />
            </label>
            <label className={s.field}>
              <span>Τι χρειάζεσαι <em>(προαιρετικό)</em></span>
              <textarea rows={2} value={form.need} onChange={set('need')}
                        placeholder="π.χ. στάζει ο θερμοσίφωνας" />
            </label>
            <button type="submit" className={s.quoteBtn}>Στείλε το αίτημα</button>
            <a href={tel} className={s.quoteAlt}>ή πάρε τηλέφωνο: {d.PHONE}</a>
          </form>
          )}
        </div>
      </header>

      {/* Landmark <main>: το Lighthouse το απαιτεί και οι screen readers
          το χρησιμοποιούν για «παράκαμψη στο περιεχόμενο». */}
      <main>
      {/* Δρομολόγηση, όχι ισχυρισμός ικανότητας: «τι δουλειά έχεις;» */}
      <section id="areas" className={s.segments} aria-label="Τι δουλειά έχεις">
        {SEGMENTS.map((seg) => (
          <a key={seg.key} href={tel} className={s.segment}>
            <span className={s.segNum} aria-hidden="true" />
            <h2>{seg.title}</h2>
            <p>{seg.desc}</p>
            <span className={s.segGo}>Ρώτησέ μας<span aria-hidden="true"> →</span></span>
          </a>
        ))}
      </section>

      {services.length > 0 && (
        <section id="services" className={s.services}>
          <header className={s.secHead}>
            {d.SERVICES_EYEBROW && <span className={s.eyebrowDark}>{d.SERVICES_EYEBROW}</span>}
            <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Τι αναλαμβάνουμε'}</h2>
          </header>
          <ol className={s.svGrid}>
            {services.map((sv, i) => (
              <li key={i} className={s.svItem}>
                <span className={s.svNum}>{String(i + 1).padStart(2, '0')}</span>
                <h3>{sv.title}</h3>
                {sv.desc && <p>{sv.desc}</p>}
                <a href={tel} className={s.svLink}>Ρώτα για τιμή<span aria-hidden="true"> →</span></a>
              </li>
            ))}
          </ol>
        </section>
      )}

      {story.length > 0 && (
        <section className={s.why}>
          <div className={s.whyInner}>
            <h2 className={s.whyTitle}>{d.STORY_TITLE || `Γιατί ${d.NAME}`}</h2>
            <div className={s.whyGrid}>
              {story.map((p, i) => (
                <p key={i} className={s.whyItem}>{p.p}</p>
              ))}
            </div>
          </div>
        </section>
      )}

      {gallery.length > 0 && (
        <section className={s.work}>
          <header className={s.secHead}>
            <h2 className={s.secTitle}>{d.GALLERY_TITLE || 'Δουλειές μας'}</h2>
          </header>
          <div className={s.workGrid}>
            {gallery.slice(0, 6).map((g, i) => (
              <figure key={i} className={s.shot}>
                <img src={g.image} alt={g.title || `${d.TRADE} — ${d.CITY}`} loading="lazy" />
                {g.title && <figcaption>{g.title}</figcaption>}
              </figure>
            ))}
          </div>
        </section>
      )}

      <section className={s.band}>
        <div className={s.bandInner}>
          <div>
            <h2 className={s.bandTitle}>{d.CTA_TITLE || 'Έχεις βλάβη τώρα;'}</h2>
            {d.HOURS && <p className={s.bandHours}>{d.HOURS}</p>}
          </div>
          <a href={tel} className={s.bandCall}>{d.PHONE}</a>
        </div>
      </section>

      </main>

      <FindUs data={d} />

      <footer className={s.footer}>
        <span>© {d.YEAR} {d.NAME}</span>
        <span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span>
        <span>Site από Vitrina</span>
      </footer>
    </div>
  )
}
