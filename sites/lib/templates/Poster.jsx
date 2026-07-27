import s from './Poster.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

export default function Poster({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <Brand data={d} className={s.logo} dark />
        <a href={tel} className={s.navCall}>{d.PHONE} ↗</a>
      </nav>

      <header id="top" className={s.hero}>
        <div className={s.heroType}>
          <span className={s.kicker}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <div className={s.outline}>{d.TRADE}</div>
        </div>
        <div className={s.heroFoot}>
          <p>{d.TAGLINE}</p>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
        </div>
      </header>

      <section id="services" className={s.svcSec}>
        <span className={s.label}>[ Υπηρεσίες ]</span>
        {d.services?.map((sv, i) => (
          <a key={i} href={tel} className={s.svc}>
            <span className={s.num}>{sv.num}</span>
            <h2>{sv.title}</h2>
            <p>{sv.desc}</p>
          </a>
        ))}
      </section>

      <section id="work" className={s.gal}>
        {d.gallery?.map((g, i) => (
          <figure key={i} className={s.galItem}>
            <img src={g.image} alt={g.title} loading="lazy" />
            <figcaption><span className={s.num}>{String(i + 1).padStart(2, '0')}</span> {g.title}</figcaption>
          </figure>
        ))}
      </section>

      <section id="story" className={s.story}>
        <span className={s.label}>[ Ποιοι είμαστε ]</span>
        <h2 className={s.quote}>{d.STORY_TITLE}</h2>
        {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
        <div className={s.sign}>— {d.NAME}</div>
      </section>

      <section id="contact" className={s.cta}>
        <a href={tel} className={s.ctaBig}>{d.CTA_TITLE}</a>
        <div className={s.ctaMeta}><span>📞 {d.PHONE}</span><span>{d.AREAS}</span></div>
      </section>

      <FindUs data={d} dark />


      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
