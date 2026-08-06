import s from './Coast.module.css'
import FindUs from './FindUs'
import Brand from './Brand'

export default function Coast({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  const g = d.gallery || []
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}><Brand data={d} /></a>
        <div className={s.links}><a href="#services">Υπηρεσίες</a><a href="#work">Γκαλερί</a><a href="#contact">Κράτηση</a></div>
        <a href={tel} className={s.navCall}>{d.PHONE}</a>
      </nav>

      <header id="top" className={s.hero}>
        <img className={s.heroBg} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
        <div className={s.heroIn}>
          <span className={s.kicker}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <p>{d.TAGLINE}</p>
          <a href={tel} className={s.btn}>📞 {d.PHONE}</a>
        </div>
      </header>

      <div className={s.strip}>
        <span>☀️ {d.CITY}</span><span>🕒 {d.HOURS}</span><span>📍 {d.AREAS}</span>
      </div>

      {/* zigzag feature rows */}
      <section id="services" className={s.zig}>
        {d.services?.map((sv, i) => (
          <div key={i} className={s.zrow}>
            {g.length > 0 && <figure className={s.zimg}><img src={g[i % g.length].image} alt={sv.title} loading="lazy" /></figure>}
            <div className={s.ztxt}>
              <span className={s.num}>{sv.num}</span>
              <h2>{sv.title}</h2>
              <p>{sv.desc}</p>
              <a href={tel} className={s.link}>Ρώτησέ μας →</a>
            </div>
          </div>
        ))}
      </section>

      <section id="work" className={s.galSec}>
        <div className={s.head}><span className={s.kicker}>Γκαλερί</span><h2>Μια ματιά.</h2></div>
        <div className={s.gal}>
          {g.map((it, i) => (
            <figure key={i}><img src={it.image} alt={it.title} loading="lazy" /><figcaption>{it.title}</figcaption></figure>
          ))}
        </div>
      </section>

      <section id="story" className={s.story}>
        <div>
          <span className={s.kicker}>Η ιστορία μας</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>
        <figure className={s.storyImg}><img src={d.STORY_IMAGE} alt={d.NAME} /></figure>
      </section>

      <section id="contact" className={s.cta}>
        <h2>{d.CTA_TITLE}</h2>
        <p>{d.AREAS}</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </section>

      <FindUs data={d} />


      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
