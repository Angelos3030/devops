import s from './Bloom.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

// "Bloom" — καφέ/ζαχαροπλαστείο/λουλούδια: πρωινό φως, στρογγυλεμένη Comfortaa,
// βοτανικό πράσινο + ροδακινί. Signature: οι καμάρες — φωτογραφίες σε arch mask
// (σαν βιτρίνα φούρνου) και πλήρως οργανικά, φιλικά σχήματα παντού.
export default function Bloom({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} />
        <span className={s.navHours}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroText}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <div className={s.heroBtns}>
            <a href={tel} className={s.cta}>Πάρε μας τηλέφωνο</a>
            <a href="#treats" className={s.ctaSoft}>Δες τα καλούδια ↓</a>
          </div>
        </div>
        {d.HERO_IMAGE && (
          <figure className={s.arch}>
            <img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
          </figure>
        )}
      </header>

      <section id="treats" className={s.treats}>
        <h2 className={s.secTitle}>Τι θα βρεις εδώ</h2>
        <div className={s.treatGrid}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.treat}>
              <span className={s.treatDot}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="gallery" className={s.windows}>
        {d.gallery?.map((g, i) => (
          <figure key={i} className={s.windowItem}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <div className={s.storyCard}>
          <span className={s.eyebrow}>Η ιστορία μας</span>
          <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <span className={s.sig}>♥ {d.NAME}</span>
        </div>
        {d.STORY_IMAGE && (
          <figure className={s.archSmall}>
            <img src={d.STORY_IMAGE} alt={d.NAME} loading="lazy" />
          </figure>
        )}
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
