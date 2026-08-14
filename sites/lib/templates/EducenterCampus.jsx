import s from './EducenterCampus.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Educenter Campus" — φροντιστήρια, κέντρα ξένων γλωσσών, εκπαίδευση, σεμινάρια.
//
// PORT από: https://github.com/themefisher/educenter-bootstrap
// LICENSE: MIT (Themefisher, 2016–present) — επαληθεύτηκε στο ίδιο το αρχείο
// LICENSE του repository, όχι από badge. Η άδεια απαιτεί διατήρηση της
// σημείωσης πνευματικών δικαιωμάτων· βλ. `licenses/THIRD-PARTY.md`.
//
// ΤΙ ΚΡΑΤΗΘΗΚΕ (σχεδιαστική λογική): η ακαδημαϊκή ηρεμία με ζεστό υπόβαθρο, το
// hero που ζευγαρώνει αξίωση με ΠΡΑΚΤΙΚΗ πληροφορία (ωράριο/εγγραφή), ο
// κατάλογος μαθημάτων ως αριθμημένες κάρτες, και η ζώνη «πώς γίνεται» σε τρία
// βήματα πριν την επικοινωνία.
//
// ΤΙ ΔΕΝ ΜΕΤΑΦΕΡΘΗΚΕ: καμία demo φωτογραφία, κανένα λογότυπο, κανένα κείμενο,
// καμία ψεύτικη στατιστική. Το πρωτότυπο δείχνει «5000+ σπουδαστές» και
// «97% επιτυχία» — τέτοιοι αριθμοί απαγορεύονται χωρίς απόδειξη στο intake
// (docs/ai/DECISIONS.md §D4). Η ζώνη αριθμών εδώ δείχνει ΜΟΝΟ δηλωμένα
// στοιχεία: πλήθος μαθημάτων, περιοχές, ωράριο.

export default function EducenterCampus({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []
  const areas = String(d.AREAS || '').split('·').map((x) => x.trim()).filter(Boolean)

  // Η ζώνη «με μια ματιά» χτίζεται ΜΟΝΟ από όσα δήλωσε ο πελάτης. Κενό πεδίο
  // δεν γίνεται μηδενικό — φεύγει.
  const facts = [
    services.length && [String(services.length), services.length === 1 ? 'πρόγραμμα' : 'προγράμματα'],
    areas.length > 1 && [String(areas.length), 'περιοχές'],
    d.HOURS && [d.HOURS, 'ωράριο'],
  ].filter(Boolean)

  const steps = [
    ['Γνωριμία', 'Μιλάμε για το επίπεδο και τον στόχο, χωρίς κόστος.'],
    ['Πρόγραμμα', 'Προτείνουμε τμήμα και ώρες που ταιριάζουν στο πρόγραμμά σου.'],
    ['Παρακολούθηση', 'Τακτική ενημέρωση για την πορεία, με σαφή εικόνα.'],
  ]

  return (
    <div className={s.root}>
      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#programs">Προγράμματα</a>
          <a href="#how">Πώς γίνεται</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
        {tel && <a href={tel} className={s.navCta}>{d.PRIMARY_CTA || 'Κλείσε γνωριμία'}</a>}
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroCopy}>
          <p className={s.eyebrow}>{d.KICKER || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          <h1 className={s.title}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
          {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}
          <div className={s.heroActions}>
            {tel && <a href={tel} className={s.primary}>{d.PRIMARY_CTA || 'Κλείσε γνωριμία'}</a>}
            <a href="#programs" className={s.secondary}>Δες τα προγράμματα</a>
          </div>
        </div>
        {/* Κάρτα εγγραφής: πρακτική πληροφορία δίπλα στην αξίωση, όχι διακόσμηση. */}
        <aside className={s.enrol}>
          <h2 className={s.enrolTitle}>Πληροφορίες εγγραφής</h2>
          <dl className={s.enrolList}>
            {d.HOURS && <div><dt>Ωράριο</dt><dd>{d.HOURS}</dd></div>}
            {(d.AREAS || d.CITY) && <div><dt>Περιοχές</dt><dd>{d.AREAS || d.CITY}</dd></div>}
            {d.PHONE && <div><dt>Τηλέφωνο</dt><dd><a href={tel}>{d.PHONE}</a></dd></div>}
            {d.EMAIL && <div><dt>Email</dt><dd><a href={`mailto:${d.EMAIL}`}>{d.EMAIL}</a></dd></div>}
          </dl>
        </aside>
      </header>

      {facts.length > 0 && (
        <div className={s.facts}>
          {facts.map(([big, small]) => (
            <div className={s.fact} key={small}><strong>{big}</strong><span>{small}</span></div>
          ))}
        </div>
      )}

      <main>
        <section id="programs" className={s.programs}>
          <header className={s.secHead}>
            <p className={s.eyebrow}>{d.SERVICES_EYEBROW || 'Τι διδάσκουμε'}</p>
            <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Προγράμματα σπουδών'}</h2>
          </header>
          <ol className={s.programGrid}>
            {services.map((sv, i) => (
              <li className={s.program} key={sv.title + i}>
                <span className={s.programNum}>{String(i + 1).padStart(2, '0')}</span>
                <h3>{sv.title}</h3>
                {sv.desc && <p>{sv.desc}</p>}
                {tel && <a href={tel} className={s.programLink}>Ρώτησε για τμήματα<span aria-hidden="true"> →</span></a>}
              </li>
            ))}
          </ol>
          {d.SERVICES_TOTAL > services.length && (
            <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρώτησέ μας</p>
          )}
        </section>

        <section id="how" className={s.how}>
          <h2 className={s.howTitle}>Πώς ξεκινάς</h2>
          <ol className={s.steps}>
            {steps.map(([t, p], i) => (
              <li key={t}><span aria-hidden="true">{i + 1}</span><h3>{t}</h3><p>{p}</p></li>
            ))}
          </ol>
        </section>

        {(story.length > 0 || d.INTRO) && (
          <section className={s.story}>
            <div className={s.storyIn}>
              <h2 className={s.storyTitle}>{d.STORY_TITLE || `Το ${d.NAME}`}</h2>
              {(story.length ? story.map((p) => p.p) : [d.INTRO]).map((text, i) => (
                <p key={i}>{text}</p>
              ))}
            </div>
            {gallery[0] && (
              <figure className={s.storyFig}>
                <img src={gallery[0].image} alt={gallery[0].title || d.NAME} loading="lazy" />
                {gallery[0].illustrative && <figcaption>Ενδεικτική εικόνα</figcaption>}
              </figure>
            )}
          </section>
        )}

        {gallery.length > 1 && (
          <section className={s.gallery} aria-label={d.GALLERY_TITLE || 'Ο χώρος μας'}>
            <h2 className={s.secTitle}>{d.GALLERY_TITLE || 'Ο χώρος μας'}</h2>
            <div className={s.galleryGrid}>
              {gallery.slice(1, 5).map((g, i) => (
                <figure key={i}>
                  <img src={g.image} alt={g.title || d.NAME} loading="lazy" />
                  <figcaption>{g.title}{g.illustrative ? ' · Ενδεικτική εικόνα' : ''}</figcaption>
                </figure>
              ))}
            </div>
          </section>
        )}

        <section className={s.cta}>
          <h2>{d.CTA_TITLE || 'Ας μιλήσουμε για το επόμενο βήμα'}</h2>
          {d.HOURS && <p>{d.HOURS}</p>}
          {tel && <a href={tel} className={s.ctaBtn}>{d.PHONE}</a>}
        </section>
      </main>

      <FindUs data={d} />
      <footer className={s.footer}>
        © {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina
      </footer>
    </div>
  )
}
