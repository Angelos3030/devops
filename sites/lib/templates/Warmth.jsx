import s from './Warmth.module.css'
import Brand from './Brand'

export default function Warmth({ data: d }) {
  const tel = `tel:+${d.PHONE_INTL}`
  return (
    <div className={s.root}>
      <nav className={s.nav}>
        <a href="#top" className={s.logo}><Brand data={d} prefix={<span className={s.mark}>{d.INITIAL}</span>} /></a>
        <div className={s.links}><a href="#services">Κατάλογος</a><a href="#work">Φωτογραφίες</a><a href="#story">Η ιστορία μας</a></div>
        <a href={tel} className={s.navBtn}>Κράτηση</a>
      </nav>

      <header id="top" className={s.hero}>
        <img className={s.heroBg} src={d.HERO_IMAGE} alt={`${d.NAME} — ${d.TRADE}`} />
        <div className={s.heroIn}>
          <span className={s.eyebrow}>{d.KICKER}</span>
          <h1>{d.NAME}</h1>
          <p>{d.TAGLINE}</p>
          <span className={s.hours}>🕒 {d.HOURS}</span>
          <div className={s.actions}><a href={tel} className={s.btn}>📞 {d.PHONE}</a><a href="#work" className={s.btnLine}>Φωτογραφίες</a></div>
        </div>
      </header>

      <section id="services" className={s.menuSec}>
        <div className={s.head}><span className={s.eyebrow}>Ο κατάλογός μας</span><h2>Με μεράκι, κάθε μέρα.</h2></div>
        <div className={s.menu}>
          {d.services?.map((sv, i) => (
            <div key={i} className={s.row}><h3>{sv.title}</h3><span className={s.dots} /><p>{sv.desc}</p></div>
          ))}
        </div>
      </section>

      <section id="work" className={s.galSec}>
        <div className={s.head}><span className={s.eyebrow}>Στιγμές</span><h2>Λίγο από εμάς.</h2></div>
        <div className={s.gal}>
          {d.gallery?.map((g, i) => (
            <figure key={i}><img src={g.image} alt={g.title} loading="lazy" /><figcaption>{g.title}</figcaption></figure>
          ))}
        </div>
      </section>

      <section id="story" className={s.story}>
        <figure className={s.storyImg}><img src={d.STORY_IMAGE} alt={d.NAME} /></figure>
        <div>
          <span className={s.eyebrow}>Η ιστορία μας</span>
          <h2>{d.STORY_TITLE}</h2>
          {d.story?.map((p, i) => <p key={i}>{p.p}</p>)}
          <div className={s.sign}>— {d.NAME}</div>
        </div>
      </section>

      <section id="contact" className={s.cta}>
        <h2>Σε περιμένουμε!</h2>
        <p>{d.AREAS} · {d.HOURS}</p>
        <a href={tel} className={s.btn}>📞 Κάλεσε {d.PHONE}</a>
      </section>

      <footer className={s.footer}>© {d.YEAR} {d.NAME} — {d.CITY} · Site από Vitrina</footer>
    </div>
  )
}
