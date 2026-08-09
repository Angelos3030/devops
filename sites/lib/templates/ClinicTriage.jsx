import s from './ClinicTriage.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Clinic Triage" — αποσταγμένο από ιατρικό portal μεγάλου οργανισμού, σε κλίμακα
// ιατρείου. Signature: αμέσως κάτω από το hero, τρεις κάρτες «τι θέλεις να κάνεις»
// (ραντεβού · πού είμαστε · υπηρεσίες) — ο επισκέπτης δρομολογείται σε 3 δευτερόλεπτα
// αντί να διαβάσει. Κλείνει με σκούρα ζώνη τηλεφώνου: η μετατροπή είναι η κλήση.

const Icon = ({ name }) => {
  const paths = {
    calendar: 'M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z',
    pin: 'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0zM12 13a3 3 0 1 0 0-6 3 3 0 0 0 0 6z',
    care: 'M4 3v7a6 6 0 0 0 12 0V3M9 21a3 3 0 0 0 6 0v-4M7 3H3M17 3h4',
    shield: 'M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z',
    clock: 'M12 7v5l3 2M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
    heart: 'M20.8 5.6a5.5 5.5 0 0 0-7.8 0L12 6.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l8.8 8.8 8.8-8.8a5.5 5.5 0 0 0 0-7.8z',
    people: 'M17 20v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 10a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM23 20v-2a4 4 0 0 0-3-3.9',
  }
  return (
    <svg className={s.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor"
         strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={paths[name] || paths.shield} />
    </svg>
  )
}

const WHY_ICONS = ['shield', 'clock', 'heart', 'people']

export default function ClinicTriage({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const book = d.BOOKING_URL || tel
  const gallery = Array.isArray(d.gallery) ? d.gallery.filter((g) => g?.image) : []
  const services = Array.isArray(d.services) ? d.services : []
  const panels = services.slice(0, 3)          // εναλλασσόμενα εικόνα/κείμενο
  const rest = services.slice(3)               // ό,τι περισσεύει, σε πλέγμα
  const why = (Array.isArray(d.story) ? d.story : []).slice(0, 4)

  // Οι τρεις δρόμοι: κράτημα ραντεβού, εύρεση, ενημέρωση. Τίποτα άλλο.
  const triage = [
    { icon: 'calendar', title: d.TRIAGE_BOOK || 'Κλείσε ραντεβού', href: book,
      desc: d.HOURS || 'Επικοινώνησε μαζί μας', action: d.PRIMARY_CTA || 'Ραντεβού' },
    { icon: 'pin', title: d.TRIAGE_FIND || 'Πού θα μας βρεις', href: '#find-us',
      desc: [d.ADDRESS, d.CITY].filter(Boolean).join(', ') || d.CITY, action: 'Οδηγίες' },
    { icon: 'care', title: d.SERVICES_NAV || 'Οι υπηρεσίες μας', href: '#services',
      desc: d.AREAS || d.TRADE, action: 'Δες τι κάνουμε' },
  ]

  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.brandLink}><Brand data={d} className={s.brand} /></a>
        <div className={s.navLinks}>
          <a href="#services">{d.SERVICES_NAV || 'Υπηρεσίες'}</a>
          {why.length > 0 && <a href="#why">Γιατί εμείς</a>}
          <a href="#find-us">Επικοινωνία</a>
        </div>
        <a href={tel} className={s.navCall}>
          <Icon name="calendar" />{d.PHONE}
        </a>
      </nav>

      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && (
          <img className={s.heroImg} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
        )}
        <div className={s.heroVeil} aria-hidden="true" />
        <div className={s.heroInner}>
          {d.KICKER && <span className={s.eyebrow}>{d.KICKER}</span>}
          <h1 className={s.heroTitle}>{d.NAME}</h1>
          <p className={s.heroLede}>{d.TAGLINE}</p>
          <div className={s.heroActions}>
            <a href={book} className={s.primary}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>
            <a href="#services" className={s.secondary}>{d.SECONDARY_CTA || 'Οι υπηρεσίες μας'}</a>
          </div>
        </div>
      </header>

      {/* Το σήμα κατατεθέν: δρομολόγηση πριν την ανάγνωση. */}
      <section className={s.triage} aria-label="Γρήγορη πλοήγηση">
        {triage.map((t, i) => (
          <a key={i} href={t.href} className={s.card}>
            <span className={s.cardIcon}><Icon name={t.icon} /></span>
            <h2 className={s.cardTitle}>{t.title}</h2>
            {t.desc && <p className={s.cardDesc}>{t.desc}</p>}
            <span className={s.cardAction}>{t.action}<span aria-hidden="true"> ›</span></span>
          </a>
        ))}
      </section>

      <section id="services" className={s.panels}>
        <header className={s.secHead}>
          {d.SERVICES_EYEBROW && <span className={s.eyebrowDark}>{d.SERVICES_EYEBROW}</span>}
          <h2 className={s.secTitle}>{d.SERVICES_TITLE || 'Πώς μπορούμε να βοηθήσουμε'}</h2>
          {d.INTRO && <p className={s.secLede}>{d.INTRO}</p>}
        </header>

        {panels.map((sv, i) => {
          const img = gallery[i]?.image
          return (
            <article key={i} className={`${s.panel} ${i % 2 ? s.panelFlip : ''} ${img ? '' : s.panelPlain}`}>
              <div className={s.panelText}>
                <h3 className={s.panelTitle}>{sv.title}</h3>
                <p className={s.panelDesc}>{sv.desc}</p>
                <a href={book} className={s.panelLink}>
                  {d.PRIMARY_CTA || 'Κλείσε ραντεβού'}<span aria-hidden="true"> ›</span>
                </a>
              </div>
              {img && (
                <figure className={s.panelFig}>
                  <img src={img} alt={gallery[i].title || sv.title} loading="lazy" />
                </figure>
              )}
            </article>
          )
        })}

        {rest.length > 0 && (
          <ul className={s.restGrid}>
            {rest.map((sv, i) => (
              <li key={i} className={s.restItem}>
                <h3>{sv.title}</h3>
                <p>{sv.desc}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {why.length > 0 && (
        <section id="why" className={s.why}>
          <h2 className={s.whyTitle}>{d.STORY_TITLE || `Γιατί ${d.NAME}`}</h2>
          <div className={s.whyGrid}>
            {why.map((w, i) => (
              <div key={i} className={s.whyItem}>
                <span className={s.whyIcon}><Icon name={WHY_ICONS[i % 4]} /></span>
                <p>{w.p}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {gallery.length > 0 && (
        <section className={s.gallery}>
          <header className={s.secHead}>
            {d.GALLERY_EYEBROW && <span className={s.eyebrowDark}>{d.GALLERY_EYEBROW}</span>}
            <h2 className={s.secTitle}>{d.GALLERY_TITLE || 'Ο χώρος μας'}</h2>
          </header>
          <div className={s.galleryGrid}>
            {gallery.slice(0, 8).map((g, i) => (
              <figure key={i} className={s.shot}>
                <img src={g.image} alt={g.title || `${d.NAME} — ${d.CITY}`} loading="lazy" />
                {g.title && <figcaption>{g.title}</figcaption>}
              </figure>
            ))}
          </div>
        </section>
      )}

      {/* Contact ribbon: η μετατροπή είναι το τηλέφωνο. */}
      <section className={s.ribbon}>
        <div className={s.ribbonInner}>
          <div className={s.ribbonCol}>
            <span className={s.ribbonLabel}>{d.CTA_TITLE || 'Ραντεβού'}</span>
            <a href={tel} className={s.ribbonPhone}>{d.PHONE}</a>
          </div>
          {d.HOURS && (
            <div className={s.ribbonCol}>
              <span className={s.ribbonLabel}>Ωράριο</span>
              <span className={s.ribbonValue}>{d.HOURS}</span>
            </div>
          )}
          <a href={book} className={s.ribbonCta}>{d.PRIMARY_CTA || 'Κλείσε ραντεβού'}</a>
        </div>
      </section>

      <FindUs data={d} />

      <footer className={s.footer}>
        <span>© {d.YEAR} {d.NAME}</span>
        <span>{[d.TRADE, d.CITY].filter(Boolean).join(' · ')}</span>
        <span>Site από Vitrina</span>
      </footer>
    </div>
  )
}
