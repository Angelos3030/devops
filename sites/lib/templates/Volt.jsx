import s from './Volt.module.css'
import Brand from './Brand'

// "Volt" — γυμναστήρια/trainers: σκούρο ανθρακί + electric lime, γεωμετρική Syne.
// Signature: οι διαγώνιες τομές (clip-path) στα sections — κίνηση/ενέργεια στη δομή.
export default function Volt({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.brand} dark />
        <span className={s.navHours}>{d.HOURS}</span>
        <a href={tel} className={s.navCall}>Δοκιμαστικό</a>
      </nav>

      <header id="top" className={s.hero}>
        {d.HERO_IMAGE && <img className={s.heroBg} src={d.HERO_IMAGE} alt="" aria-hidden="true" />}
        <div className={s.heroShade} aria-hidden="true" />
        <div className={s.heroIn}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1 className={s.title}>{d.NAME}</h1>
          <p className={s.lede}>{d.TAGLINE}</p>
          <a href={tel} className={s.cta}>Κλείσε δωρεάν δοκιμαστικό</a>
        </div>
      </header>

      <section id="training" className={s.svc}>
        <h2 className={s.secTitle}>Προπόνηση</h2>
        <div className={s.svcGrid}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.card}>
              <span className={s.cardNum}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="floor" className={s.floor}>
        {d.gallery?.slice(0, 4).map((g, i) => (
          <figure key={i} className={s.shot}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption>{g.title}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <h2 className={s.storyTitle}>{d.STORY_TITLE}</h2>
        <div className={s.storyCols}>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
        </div>
      </section>

      <section id="contact" className={s.cta2}>
        <h2>{d.CTA_TITLE}</h2>
        <a href={tel} className={s.cta}>📞 {d.PHONE}</a>
        <p className={s.cta2Sub}>{d.HOURS} · {d.AREAS}</p>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} · {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
