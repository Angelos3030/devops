import s from './Pulse.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Pulse" — ιατρεία/κλινικές: κλινική ηρεμία. Λευκό + teal, απαλές γωνίες,
// ραντεβού-πρώτα. Signature: η γραμμή παλμού (ECG hairline) που διατρέχει τα
// sections — διακριτικό σήμα φροντίδας, όχι διακόσμηση.
export default function Pulse({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} />
        <span className={s.navHours}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>Κλείσε ραντεβού</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.heroRow}>
            <a href={tel} className={s.cta}>📞 {d.PHONE}</a>
            <span className={s.softNote}>Απαντάμε άμεσα · χωρίς αναμονές</span>
          </div>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      <div className={s.pulseLine} aria-hidden="true"><svg viewBox="0 0 600 40" preserveAspectRatio="none"><path d="M0 20 H230 L245 6 L262 34 L276 12 L288 20 H600" fill="none" stroke="currentColor" strokeWidth="1.6" /></svg></div>

      <section id="services" className={s.svc}>
        <div className={s.secHead}>
          <span className={s.eyebrow}>Υπηρεσίες</span>
          <h2>Πώς μπορούμε να βοηθήσουμε</h2>
        </div>
        <div className={s.svcGrid}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.card}>
              <span className={s.cardNum}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
              <a href={tel} className={s.cardLink}>Ραντεβού →</a>
            </div>
          ))}
        </div>
      </section>

      <section id="space" className={s.spaces}>
        {d.gallery?.slice(0, 4).map((g, i) => (
          <figure key={i} className={s.space}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <div className={s.storyIn}>
          <span className={s.eyebrowLight}>Η φιλοσοφία μας</span>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <span className={s.sig}>{d.NAME} · {d.CITY}</span>
        </div>
      </section>

      <section id="contact" className={s.cta2}>
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.cta}>📞 {d.PHONE}</a>
        <p className={s.cta2Sub}>{d.HOURS} · {d.AREAS}</p>
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
