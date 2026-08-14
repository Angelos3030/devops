import s from './AirspaceOffice.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Airspace Office" — σύμβουλοι, αρχιτέκτονες, μηχανικοί, επαγγελματικές υπηρεσίες.
//
// PORT από: https://github.com/themefisher/airspace-hugo
// LICENSE: MIT (Themefisher, 2018–present) — επαληθεύτηκε στο αρχείο LICENSE του
// repository. Απαιτείται διατήρηση σημείωσης· βλ. `licenses/THIRD-PARTY.md`.
//
// ΤΙ ΚΡΑΤΗΘΗΚΕ: ο αέρας. Το Airspace πουλάει σοβαρότητα μέσα από κενό χώρο και
// λεπτές γραμμές, όχι μέσα από όγκο. Κρατήθηκαν: το hero που ζευγαρώνει μεγάλη
// δήλωση με στήλη στοιχείων, οι υπηρεσίες ως ΣΕΙΡΕΣ με λεπτό διαχωριστικό (όχι
// κάρτες), και το ήσυχο κλείσιμο χωρίς κραυγή.
//
// ΤΙ ΔΕΝ ΜΕΤΑΦΕΡΘΗΚΕ: demo φωτογραφίες, λογότυπα πελατών, testimonials και
// counters. Τα «100+ projects» και τα λογότυπα συνεργατών του πρωτοτύπου είναι
// ακριβώς οι ισχυρισμοί που απαγορεύει το docs/ai/DECISIONS.md §D4 χωρίς
// δεδομένα — και τα logos θα ήταν και σήματα τρίτων.

export default function AirspaceOffice({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 3) : []
  const meta = [
    d.TRADE && ['Αντικείμενο', d.TRADE],
    (d.AREAS || d.CITY) && ['Περιοχές', d.AREAS || d.CITY],
    d.HOURS && ['Ωράριο', d.HOURS],
  ].filter(Boolean)

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#services">Υπηρεσίες</a>
          <a href="#approach">Προσέγγιση</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
        {tel && <a href={tel} className={s.navCta}>{d.PRIMARY_CTA || 'Κλείσε συνάντηση'}</a>}
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroMain}>
          <p className={s.eyebrow}>{d.KICKER || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          <h1 className={s.title}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
          {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}
          <div className={s.heroActions}>
            {tel && <a href={tel} className={s.primary}>{d.PRIMARY_CTA || 'Κλείσε συνάντηση'}</a>}
            <a href="#services" className={s.textLink}>Τι αναλαμβάνουμε<span aria-hidden="true"> →</span></a>
          </div>
        </div>
        {meta.length > 0 && (
          <dl className={s.heroMeta}>
            {meta.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}
          </dl>
        )}
      </header>

      {gallery[0] && (
        <figure className={s.band}>
          <img src={gallery[0].image} alt={gallery[0].title || d.NAME} />
          {gallery[0].illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
        </figure>
      )}

      <main>
        <section id="services" className={s.services}>
          <header className={s.secHead}>
            <p className={s.eyebrow}>{d.SERVICES_EYEBROW || 'Υπηρεσίες'}</p>
            <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Πού μπορούμε να βοηθήσουμε'}</h2>
          </header>
          {/* Σειρές, όχι κάρτες: με 2 ή με 9 υπηρεσίες η στήλη διαβάζεται ίδια. */}
          <ol className={s.rows}>
            {services.map((sv, i) => (
              <li className={s.row} key={sv.title + i}>
                <span className={s.rowNum}>{String(i + 1).padStart(2, '0')}</span>
                <h3>{sv.title}</h3>
                {sv.desc && <p>{sv.desc}</p>}
                {tel && <a href={tel} className={s.rowLink}>Συζήτησέ το<span aria-hidden="true"> →</span></a>}
              </li>
            ))}
          </ol>
          {d.SERVICES_TOTAL > services.length && (
            <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρωτήστε μας</p>
          )}
        </section>

        <section id="approach" className={s.approach}>
          <div className={s.approachIn}>
            <h2 className={s.approachTitle}>{d.STORY_TITLE || 'Πώς δουλεύουμε'}</h2>
            <div className={s.approachCols}>
              {(story.length ? story.map((p) => p.p) : [d.INTRO].filter(Boolean)).map((text, i) => (
                <p key={i}>{text}</p>
              ))}
            </div>
          </div>
        </section>

        {gallery.length > 1 && (
          <section className={s.work} aria-label={d.GALLERY_TITLE || 'Δουλειές μας'}>
            <h2 className={s.secTitle}>{d.GALLERY_TITLE || 'Δουλειές μας'}</h2>
            <div className={s.workGrid}>
              {gallery.slice(1, 4).map((g, i) => (
                <figure key={i}>
                  <img src={g.image} alt={g.title || d.NAME} loading="lazy" />
                  <figcaption>{g.title}{g.illustrative ? ' · Ενδεικτική εικόνα' : ''}</figcaption>
                </figure>
              ))}
            </div>
          </section>
        )}

        <section className={s.cta}>
          <div className={s.ctaIn}>
            <h2>{d.CTA_TITLE || 'Ας συζητήσουμε το επόμενο βήμα'}</h2>
            <div className={s.ctaLinks}>
              {tel && <a href={tel} className={s.ctaPhone}>{d.PHONE}</a>}
              {d.EMAIL && <a href={`mailto:${d.EMAIL}`} className={s.textLink}>{d.EMAIL}</a>}
            </div>
          </div>
        </section>
      </main>

      <FindUs data={d} />
      <footer className={s.footer}>
        © {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina
      </footer>
    </div>
  )
}
