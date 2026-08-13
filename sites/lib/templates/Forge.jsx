import s from './Forge.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Forge" — τεχνίτες (υδραυλικός/ηλεκτρολόγος/μάστορας): φως ημέρας βιομηχανικό,
// ατσάλι + safety yellow. Signature: hazard-stripe άξονας + trust band (χρόνια,
// εγγύηση, 24/7) — ο πελάτης εδώ θέλει σιγουριά & άμεσο τηλέφωνο, όχι ποίηση.
export default function Forge({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const primaryArea = String(d.AREAS || d.CITY || 'Η περιοχή σας').split('·')[0].trim()
  // Μόνο δηλωμένα γεγονότα. Καμία εγγύηση, κανένας χρόνος απόκρισης, καμία τιμή.
  const areaList = String(d.AREAS || '').split('·').map((x) => x.trim()).filter(Boolean)
  const trust = [
    d.TRADE && [d.TRADE, d.CITY || ''],
    d.HOURS && ['Ωράριο', d.HOURS],
    areaList.length > 1 ? [primaryArea, `& ${areaList.length - 1} ακόμη περιοχές`]
      : (d.CITY && [primaryArea, 'και γύρω περιοχές']),
    d.PHONE && ['Τηλέφωνο', d.PHONE],
  ].filter(Boolean)
  return (
    <div className={s.root}>
      <div className={s.stripe} aria-hidden="true" />
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} />
        <span className={s.navHours}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>📞 {d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.heroBtns}>
            <a href={tel} className={s.cta}>Κάλεσε τώρα</a>
            <a href="#work" className={s.ctaGhost}>Δες δουλειές</a>
          </div>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      {/* Η ζώνη έλεγε «Εγγύηση σε κάθε εργασία» και «Καθαρές τιμές από πριν» σε
          ΚΑΘΕ πελάτη που πήρε αυτό το theme — ισχυρισμοί που κανείς δεν είχε
          δηλώσει. Τώρα δείχνει μόνο δηλωμένα στοιχεία, και ό,τι λείπει απλώς
          δεν εμφανίζεται. Βλ. docs/ai/DECISIONS.md §D4. */}
      {trust.length > 0 && (
        <div className={s.trust}>
          {trust.map(([strong, sub]) => (
            <div className={s.trustItem} key={strong}><strong>{strong}</strong><span>{sub}</span></div>
          ))}
        </div>
      )}

      <section id="services" className={s.svc}>
        <h2 className={s.secTitle}>Τι αναλαμβάνω</h2>
        <div className={s.svcGrid}>
          {d.services?.map((sv, i) => (
            <a key={i} href={tel} className={s.card}>
              <span className={s.cardNum}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
              <span className={s.cardCall}>Κάλεσε →</span>
            </a>
          ))}
        </div>
      </section>

      <section id="work" className={s.work}>
        <h2 className={s.secTitle}>Πρόσφατες δουλειές</h2>
        <div className={s.workGrid}>
          {d.gallery?.map((g, i) => (
            <figure key={i} className={s.shot}>
              <img src={g.image} alt={g.title} loading="lazy" />
              <figcaption><strong>{g.title}</strong><span>{g.sub}</span></figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section className={s.story}>
        <div className={s.storyIn}>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
        </div>
        {d.STORY_IMAGE && <figure className={s.storyFig}><img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" /></figure>}
      </section>

      <section id="contact" className={s.cta2}>
        <div className={s.stripe} aria-hidden="true" />
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.ctaBig}>📞 {d.PHONE}</a>
        <p className={s.cta2Sub}>{d.HOURS} · {d.AREAS}</p>
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
