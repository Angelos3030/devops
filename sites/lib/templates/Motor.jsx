import s from './Motor.module.css'
import Brand from './Brand'

// "Motor" — συνεργεία: σκοτεινό γκαράζ, signal κόκκινο, τεχνικό mono. Signature:
// το δελτίο εργασιών — υπηρεσίες σαν service checklist με τετράγωνα κουτάκια ✓.
export default function Motor({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} dark />
        <span className={s.navHours}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>📞 {d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.badges}>
            <span className={s.badge}>✓ Γραπτή εγγύηση</span>
            <span className={s.badge}>✓ Τιμή πριν την εργασία</span>
          </div>
          <a href={tel} className={s.cta}>Κλείσε ραντεβού</a>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.heroFig}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      <section id="services" className={s.sheet}>
        <div className={s.sheetHead}>
          <h2>Δελτίο εργασιών</h2>
          <span className={s.sheetNo}>Νο. {d.YEAR}</span>
        </div>
        <ul className={s.checks}>
          {d.services?.map((sv, i) => (
            <li key={i} className={s.check}>
              <span className={s.box} aria-hidden="true">✓</span>
              <div>
                <h3>{sv.title}</h3>
                <p>{sv.desc}</p>
              </div>
              <a href={tel} className={s.checkCall}>Ρώτα μας →</a>
            </li>
          ))}
        </ul>
      </section>

      <section id="work" className={s.shots}>
        {d.gallery?.slice(0, 4).map((g, i) => (
          <figure key={i} className={s.shot}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
        {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
      </section>

      <section id="contact" className={s.cta2}>
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.ctaBig}>📞 {d.PHONE}</a>
        <p className={s.cta2Sub}>{d.HOURS} · {d.AREAS}</p>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
