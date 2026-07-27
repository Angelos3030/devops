import s from './Showcase.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

export default function Showcase({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}><Brand data={d} /></a>
        <a href={tel} className={s.navCall}>📞 {d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <img className={s.heroBg} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
        <div className={s.heroIn}>
          <span className={s.kicker}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <p>{d.TAGLINE}</p>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
        </div>
        <div className={s.scroll}>SCROLL</div>
      </header>

      {/* gallery leads — visual-first */}
      <section id="work" className={s.galWrap}>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i} className={s['g' + (i % 5)]}>
              <img src={g.image} alt={g.title} loading="lazy" />
              <figcaption><b>{g.title}</b><span>{g.sub}</span></figcaption>
            </figure>
          ))}
        </div>
      </section>

      {/* services as horizontal scroll */}
      <section id="services" className={s.services}>
        <div className={s.head}><span className={s.kicker}>Υπηρεσίες</span><h2>Τι προσφέρουμε.</h2></div>
        <div className={s.hscroll}>
          {d.services?.map((sv, i) => (
            <article key={i} className={s.card}>
              <span className={s.cnum}>{sv.num}</span>
              <h3>{sv.title}</h3><p>{sv.desc}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="story" className={s.story}>
        <img src={d.STORY_IMAGE} alt={d.NAME} className={s.storyBg} />
        <div className={s.storyCard}>
          <span className={s.kicker}>Ποιοι είμαστε</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>
      </section>

      <section id="contact" className={s.cta}>
        <h2>{d.CTA_TITLE}</h2>
        <p>Δωρεάν εκτίμηση — {d.AREAS}.</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
