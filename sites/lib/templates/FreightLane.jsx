import s from './FreightLane.module.css'
import Brand from './Brand'
import FindUs from './FindUs'

// "Freight Lane" — μεταφορές, logistics, μετακομίσεις, courier, αποθήκευση.
//
// ⚠ ΟΧΙ PORT. ΑΝΕΞΑΡΤΗΤΗ ΑΝΑΔΗΜΙΟΥΡΓΙΑ ΑΠΟ ΟΠΤΙΚΗ ΑΝΑΦΟΡΑ ΜΟΝΟ.
//
// Υποψήφιο: themixlyweb/nextjs-logistics-website-template ("FreightEdge").
// Η άδεια ΑΝΤΙΦΑΣΚΕΙ με τον εαυτό της:
//   • το αρχείο LICENSE και τα metadata του GitHub λένε MIT
//   • το README λέει «You may use this version for personal and educational
//     purposes» και δείχνει το «Commercial Use Allowed» ΜΟΝΟ στην επί πληρωμή
//     έκδοση, με το «Commercial license» αποκλειστικό της Themixly Full Version
//
// Το Vitrina πουλάει sites. Δεν μπορούμε να στηριχτούμε στην επιεικέστερη
// ανάγνωση όταν ο ίδιος ο εκδότης λέει το αντίθετο δύο αρχεία παρακάτω.
// Απόφαση: ΚΑΜΙΑ επαναχρησιμοποίηση κώδικα, markup, CSS ή asset. Κρατήθηκε μόνο
// η ΙΔΕΑ ενός logistics site — που δεν ανήκει σε κανέναν — και υλοποιήθηκε από
// το μηδέν. Βλ. `licenses/THIRD-PARTY.md`.
//
// Η δική μας σχεδιαστική απάντηση: ο πελάτης μεταφορών δεν αγοράζει αισθητική,
// αγοράζει ΒΕΒΑΙΟΤΗΤΑ. Άρα η σελίδα οργανώνεται γύρω από τρία ερωτήματα —
// τι μεταφέρεις, πού φτάνει, πότε — και το τηλέφωνο δεν φεύγει ποτέ από την οθόνη.

export default function FreightLane({ data: d }) {
  const tel = d.PHONE_INTL ? `tel:+${d.PHONE_INTL}` : ''
  const services = Array.isArray(d.services) ? d.services : []
  const gallery = (Array.isArray(d.gallery) ? d.gallery : []).filter((g) => g?.image)
  const story = Array.isArray(d.story) ? d.story.slice(0, 2) : []
  const areas = String(d.AREAS || d.CITY || '').split('·').map((x) => x.trim()).filter(Boolean)

  return (
    <div className={s.root}>
      <div className={s.utility}>
        {(d.AREAS || d.CITY) && <span>{d.AREAS || d.CITY}</span>}
        {d.HOURS && <span>{d.HOURS}</span>}
        {tel && <a href={tel}>{d.PHONE}</a>}
      </div>

      <nav className={s.nav} aria-label="Κύρια πλοήγηση">
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} dark /></a>
        <div className={s.navLinks}>
          <a href="#lanes">Υπηρεσίες</a>
          <a href="#coverage">Κάλυψη</a>
          <a href="#find-us">Επικοινωνία</a>
        </div>
        {tel && <a href={tel} className={s.navCta}>{d.PRIMARY_CTA || 'Ζήτησε προσφορά'}</a>}
      </nav>

      <header id="top" className={s.hero}>
        {gallery[0] && <img className={s.heroImg} src={gallery[0].image} alt="" aria-hidden="true" />}
        <div className={s.heroVeil} />
        <div className={s.heroIn}>
          <p className={s.eyebrow}>{d.KICKER || [d.TRADE, d.CITY].filter(Boolean).join(' · ')}</p>
          <h1 className={s.title}>{d.HERO_TITLE || d.TAGLINE || d.NAME}</h1>
          {d.INTRO && <p className={s.lede}>{d.INTRO}</p>}
          {tel && (
            <a href={tel} className={s.phoneBlock}>
              <span>Πάρε τηλέφωνο</span>
              <strong>{d.PHONE}</strong>
            </a>
          )}
        </div>
      </header>

      <main>
        {/* Οι τρεις ερωτήσεις κάθε πελάτη μεταφορών, με τη σειρά που τις σκέφτεται. */}
        <section className={s.checks}>
          <div><b>01</b><h2>Τι μεταφέρεις</h2><p>{services[0]?.title || d.TRADE}</p></div>
          <div><b>02</b><h2>Πού φτάνει</h2><p>{d.AREAS || d.CITY || '—'}</p></div>
          <div><b>03</b><h2>Πότε</h2><p>{d.HOURS || 'Κατόπιν συνεννόησης'}</p></div>
        </section>

        <section id="lanes" className={s.lanes}>
          <header className={s.secHead}>
            <p className={s.eyebrowDark}>{d.SERVICES_EYEBROW || 'Υπηρεσίες'}</p>
            <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Τι αναλαμβάνουμε'}</h2>
          </header>
          <ol className={s.laneList}>
            {services.map((sv, i) => (
              <li className={s.lane} key={sv.title + i}>
                <span className={s.laneNum}>{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <h3>{sv.title}</h3>
                  {sv.desc && <p>{sv.desc}</p>}
                </div>
                {tel && <a href={tel} className={s.laneLink}>Προσφορά<span aria-hidden="true"> →</span></a>}
              </li>
            ))}
          </ol>
          {d.SERVICES_TOTAL > services.length && (
            <p className={s.more}>+ {d.SERVICES_TOTAL - services.length} ακόμη — ρώτησέ μας</p>
          )}
        </section>

        {areas.length > 0 && (
          <section id="coverage" className={s.coverage}>
            <h2 className={s.coverageTitle}>Περιοχές που εξυπηρετούμε</h2>
            <ul className={s.areaList}>
              {areas.map((a) => <li key={a}>{a}</li>)}
            </ul>
          </section>
        )}

        {(story.length > 0 || d.INTRO) && (
          <section className={s.about}>
            <div className={s.aboutIn}>
              <h2 className={s.aboutTitle}>{d.STORY_TITLE || `Η ${d.NAME}`}</h2>
              {(story.length ? story.map((p) => p.p) : [d.INTRO]).map((text, i) => <p key={i}>{text}</p>)}
            </div>
          </section>
        )}

        {gallery.length > 1 && (
          <section className={s.fleet} aria-label={d.GALLERY_TITLE || 'Ο στόλος μας'}>
            <div className={s.fleetGrid}>
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
          <h2>{d.CTA_TITLE || 'Πες μας τι θέλεις να μεταφερθεί'}</h2>
          {tel && <a href={tel} className={s.ctaBtn}>{d.PHONE}</a>}
          {d.HOURS && <p>{d.HOURS}</p>}
        </section>
      </main>

      <FindUs data={d} />
      <footer className={s.footer}>
        © {d.YEAR} {[d.NAME, d.CITY].filter(Boolean).join(' · ')} · Site από Vitrina
      </footer>
    </div>
  )
}
