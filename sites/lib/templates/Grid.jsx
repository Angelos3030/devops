import s from './Grid.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

export default function Grid({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <header className={s.top}>
        <Brand data={d} className={s.brand} />
        <span className={s.m}>{d.TRADE}</span>
        <span className={s.m}>{d.CITY}</span>
        <a href={tel} className={s.m}>{d.PHONE} ↗</a>
      </header>

      <section className={s.hero} id="top">
        <div className={s.heroTxt}>
          <span className={s.tag}>{d.KICKER}</span>
          <h1>{d.TAGLINE}</h1>
        </div>
        <figure className={s.heroImg}><img src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} /></figure>
      </section>

      <section id="services" className={s.block}>
        <div className={s.blockHead}><span className={s.idx}>01</span><span className={s.tag}>Υπηρεσίες</span></div>
        <div className={s.rows}>
          {d.services?.map((sv, i) => (
            <a key={i} href={tel} className={s.row}>
              <span className={s.m}>{sv.num}</span>
              <h3>{sv.title}</h3>
              <p>{sv.desc}</p>
              <span className={s.arrow}>→</span>
            </a>
          ))}
        </div>
      </section>

      <section id="work" className={s.block}>
        <div className={s.blockHead}><span className={s.idx}>02</span><span className={s.tag}>Έργα</span></div>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i}>
              <img src={g.image} alt={g.title} loading="lazy" />
              <figcaption><span className={s.m}>{String(i + 1).padStart(2, '0')}</span>{g.title}</figcaption>
            </figure>
          ))}
        </div>
      </section>

      <section id="story" className={s.block}>
        <div className={s.blockHead}><span className={s.idx}>03</span><span className={s.tag}>Ποιοι είμαστε</span></div>
        <div className={s.storyGrid}>
          <h2>{d.STORY_TITLE}</h2>
          <div>{d.story?.map((p, i) => <p key={i}>{p.p}</p>)}<div className={s.sign}>— {d.NAME}</div></div>
        </div>
      </section>

      <section id="contact" className={s.cta}>
        <span className={s.tag}>Επικοινωνία</span>
        <a href={tel} className={s.ctaBig}>{d.CTA_TITLE}</a>
        <div className={s.ctaRow}><span className={s.m}>📞 {d.PHONE}</span><span className={s.m}>{d.AREAS}</span><span className={s.m}>{d.HOURS}</span></div>
      </section>

      <FindUs data={d} />


      <footer className={s.foot}><span className={s.m}>© {d.YEAR} {d.NAME}</span><span className={s.m}>{d.CITY} · Vitrina</span></footer>
    </div>
  )
}
